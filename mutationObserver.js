window.mutationRecords = [];
const form = document.querySelector("form");
if (!form) {
    console.warn("No form found. Skipping mutation observer injection.");
} else {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            window.mutationRecords.push({
                type: mutation.type,
                target: mutation.target.outerHTML,
                addedNodes: Array.from(mutation.addedNodes).map(node => node.outerHTML),
                removedNodes: Array.from(mutation.removedNodes).map(node => node.outerHTML),
                attributeChanges: mutation.attributeName ? mutation.attributeName + ' changed' : ''
            });
        });
    });

    observer.observe(form, { attributes: true, childList: true, subtree: true });
}