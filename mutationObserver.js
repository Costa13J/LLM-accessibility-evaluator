window.mutationRecords = window.mutationRecords || [];
window.mutationLogSize = 0;  
const MAX_MUTATION_LOG_SIZE = 300000; 
let noiseFilterEnabled = false;

function findAssociatedFieldInfo(target) {
    let field = target;
    while (field && !['INPUT', 'TEXTAREA', 'SELECT'].includes(field.tagName)) {
        field = field.parentElement;
    }
    if (!field) return {};

    const name = field.getAttribute('name') || '';
    const id = field.id || '';
    const type = field.getAttribute('type') || '';
    const autocomplete = field.getAttribute('autocomplete') || '';

    

    // Filter: Skip metadata-like fields
    const noisyPatterns = ["token", "honeypot", "build"];
    if (
        type === "hidden" ||
        noisyPatterns.some(p => name.toLowerCase().includes(p)) ||
        ["off", "new-password"].includes(autocomplete)
    ) {
        return { skip: true, reason: `Ignored: metadata field (${name || type})` };
    }

    // Filter: Skip <select> with too many options
    if (field.tagName === 'SELECT' && field.options.length > 5) {
        return { skip: true, reason: "Ignored: select with too many options" };
    }

    // Try to get label and describedBy text
    const describedBy = field.getAttribute("aria-describedby") || '';
    let describedText = '';

    if (describedBy) {
        describedText = describedBy
            .split(/\s+/)
            .map(id => {
                const el = document.getElementById(id);
                return el?.innerText?.trim();
            })
            .filter(Boolean)
            .join(" ");
    }

    let label = '';
    if (id) {
        const labelElem = document.querySelector(`label[for="${id}"]`);
        if (labelElem) label = labelElem.innerText.trim();
    }
    if (!label && field.closest('label')) {
        label = field.closest('label').innerText.trim();
    }

    return {
        field,
        fieldName: name,
        fieldId: id,
        fieldLabel: label,
        ariaDescribedText: describedText,
        skip: false,
        reason: "Valid mutation"
    };
}

const observer = new MutationObserver(function (mutationsList) {
    for (const mutation of mutationsList) {
        const target = mutation.target;

        const serializedTarget = target.outerHTML || target.textContent || "";
        window.mutationLogSize += serializedTarget.length;

        if (!noiseFilterEnabled && window.mutationLogSize > MAX_MUTATION_LOG_SIZE) {
            console.warn("High mutation volume detected — enabling noise filtering.");
            noiseFilterEnabled = true;
        }

        if (noiseFilterEnabled && !target.closest('form')) {
            window.mutationRecords.push({
                type: mutation.type,
                reasonCode: "Ignored: mutation outside form",
                timestamp: new Date().toISOString()
            });
            continue;
        }

        const fieldInfo = findAssociatedFieldInfo(target);

        if (fieldInfo.skip) {
            window.mutationRecords.push({
                type: mutation.type,
                reasonCode: fieldInfo.reason,
                timestamp: new Date().toISOString()
            });
            continue;
        }

        const record = {
            type: mutation.type,
            target: target.outerHTML || "",
            targetTag: target.tagName,
            targetId: target.id || "",
            targetClass: target.className || "",
            attributeChanged: "",
            newValue: "",
            validationFlag: false,
            addedNodes: [],
            removedNodes: [],
            possibleErrorMessages: [],
            timestamp: new Date().toISOString(),
            ariaDescribedText: fieldInfo.ariaDescribedText || "",
            reasonCode: fieldInfo.reason
        };

        if (mutation.type === "childList") {
            for (const node of mutation.addedNodes) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const text = node.innerText?.trim();
                    const isOption = node.tagName === "OPTION";
                    const isLong = text?.length > 300;
                    const isEmpty = !text || /^\s*$/.test(text);
                    const isAutocomplete = node.className?.includes("autocomplete") || node.role === "option";

                    if (isOption || isLong || isEmpty || isAutocomplete) continue;

                    record.possibleErrorMessages.push(text);
                    record.addedNodes.push(node.outerHTML);
                }
            }

            for (const node of mutation.removedNodes) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    record.removedNodes.push(node.outerHTML);
                }
            }
        } else if (mutation.type === "attributes") {
            const attrName = mutation.attributeName;
            record.attributeChanged = attrName;
            record.newValue = target.getAttribute(attrName);

            if (["style", "class"].includes(attrName)) {
                const visibleText = target.innerText?.trim();
                if (visibleText && visibleText.length < 300) {
                    record.possibleErrorMessages.push(visibleText);
                    record.validationFlag = true;
                }
            }

            if (attrName === "aria-invalid" || attrName === "aria-describedby") {
                record.validationFlag = true;
            }
        }

        window.mutationRecords.push(record);
    }
});

observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["style", "class", "aria-invalid", "aria-describedby"],
    childList: true,
    subtree: true
});