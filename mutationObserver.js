window.mutationRecords = [];

function findAssociatedFieldInfo(target) {
    let field = target;

    // If the target is not a form control, try to walk up the DOM
    while (field && !['INPUT', 'TEXTAREA', 'SELECT'].includes(field.tagName)) {
        field = field.parentElement;
    }

    if (!field) return {};

    const name = field.getAttribute('name') || '';
    const id = field.id || '';

    // Try to find a label
    let label = '';
    if (id) {
        const labelElem = document.querySelector(`label[for="${id}"]`);
        if (labelElem) label = labelElem.innerText.trim();
    }

    // If no label found via `for`, check for wrapping label
    if (!label && field.closest('label')) {
        label = field.closest('label').innerText.trim();
    }

    return { fieldName: name, fieldId: id, fieldLabel: label };
}

const observer = new MutationObserver(function (mutationsList) {
    for (const mutation of mutationsList) {
        const fieldInfo = findAssociatedFieldInfo(mutation.target);

        const record = {
            type: mutation.type,
            target: mutation.target.outerHTML || "",
            targetTag: mutation.target.tagName,
            targetId: mutation.target.id || "",
            targetClass: mutation.target.className || "",
            attributeChanged: "",
            newValue: "",
            validationFlag: false,
            addedNodes: [],
            removedNodes: [],
            possibleErrorMessages: [],
            timestamp: new Date().toISOString(),
            fieldName: fieldInfo.fieldName || "",
            fieldId: fieldInfo.fieldId || "",
            fieldLabel: fieldInfo.fieldLabel || "",
        };

        if (mutation.type === "childList") {
            for (const node of mutation.addedNodes) {
                if (node.nodeType === Node.ELEMENT_NODE) {
                    const text = node.innerText?.trim();
                    if (text) {
                        record.possibleErrorMessages.push(text);
                        record.addedNodes.push(node.outerHTML);
                    }
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
            record.newValue = mutation.target.getAttribute(attrName);

            

            if (["style", "class"].includes(attrName)) {
                const visibleText = mutation.target.innerText?.trim();
                if (visibleText) {
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

// Track attribute and childList changes more deeply
observer.observe(document.body, {
    attributes: true,
    attributeFilter: ["style", "class", "aria-invalid", "aria-describedby"],
    childList: true,
    subtree: true
});
