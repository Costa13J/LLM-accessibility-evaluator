window.mutationRecords = window.mutationRecords || [];
window.mutationLogSize = 0;
const MAX_MUTATION_LOG_SIZE = 300000;

// Cache of previous styles to diff before/after
const previousStyles = new WeakMap();

function getRelevantStyles(el) {
    const s = window.getComputedStyle(el);
    const visualCues = [
        "border-color",
        "background-color",
        "color",
        "outline-color",
        "box-shadow"
    ];
    const out = {};
    for (const prop of visualCues) {
        out[prop] = s.getPropertyValue(prop);
    }
    return out;
}

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

    // Skip metadata-like fields
    const noisyPatterns = ["token", "honeypot", "build"];
    if (
        type === "hidden" ||
        noisyPatterns.some(p => name.toLowerCase().includes(p)) ||
        ["off", "new-password"].includes(autocomplete)
    ) {
        return { skip: true, reason: `Ignored: metadata field (${name || type})` };
    }

    // Skip <select> with too many options (was problematic)
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

        const fieldInfo = findAssociatedFieldInfo(target);
        if (fieldInfo.skip) continue;

        const record = {
            type: mutation.type,
            targetTag: target.tagName,
            targetId: target.id || "",
            targetClass: target.className || "",
            attributeChanged: "",
            oldValue: "",
            newValue: "",
            validationFlag: false,
            addedNodes: [],
            removedNodes: [],
            possibleErrorMessages: [],
            timestamp: new Date().toISOString(),
            ariaDescribedText: fieldInfo.ariaDescribedText || "",
            reasonCode: fieldInfo.reason,
            errorClasses: [],
            computedColorStyles: {} // before/after
        };

        // Attributes
        if (mutation.type === "attributes") {
            const attrName = mutation.attributeName;
            record.attributeChanged = attrName;
            record.oldValue = mutation.oldValue || "";
            record.newValue = target.getAttribute(attrName);

            if (["style", "class", "hidden", "data-error"].includes(attrName)) {
                const before = previousStyles.get(target) || {};
                const after = getRelevantStyles(target);
                previousStyles.set(target, after);

                record.computedColorStyles = { before, after };

                // Detect error classes
                const errorClassKeywords = ["error", "invalid", "danger", "highlight"];
                record.errorClasses = target.className
                    .split(/\s+/)
                    .filter(c => errorClassKeywords.some(k => c.toLowerCase().includes(k)));

                // Look for nearby/sibling text cues (not just parent)
                const siblingText = target.nextElementSibling?.innerText?.trim();
                const parentText = target.parentElement?.innerText?.trim();
                [siblingText, parentText].forEach(txt => {
                    if (txt && txt.length < 300) {
                        record.possibleErrorMessages.push(txt);
                    }
                });

                if (record.possibleErrorMessages.length > 0 || record.errorClasses.length > 0) {
                    record.validationFlag = true;
                }
            }

            if (["aria-invalid", "aria-describedby"].includes(attrName)) {
                record.validationFlag = true;
            }
        }

        // ChildList (new error messages)
        if (mutation.type === "childList") {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const text = node.innerText?.trim();
                    if (text) {
                        record.possibleErrorMessages.push(text);
                        record.validationFlag = true;
                        record.addedNodes.push(node.outerHTML || "");
                    }
                }
            });

            mutation.removedNodes.forEach(node => {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    record.removedNodes.push(node.outerHTML || "");
                }
            });
        }

        // Capture natively invalid fields after submit
        if (mutation.type === "childList" || mutation.type === "attributes") {
            document.querySelectorAll("input:invalid, textarea:invalid, select:invalid")
                .forEach(invalidEl => {
                    const msg = invalidEl.validationMessage; // native browser message
                    if (msg) {
                        record.possibleErrorMessages.push(msg);
                        record.validationFlag = true;
                    }
                });
        }

        window.mutationRecords.push(record);
    }
});

observer.observe(document.body, {
    attributes: true,
    attributeOldValue: true,
    attributeFilter: ["style", "class", "hidden", "aria-invalid", "aria-describedby", "data-error"],
    childList: true,
    subtree: true
});

