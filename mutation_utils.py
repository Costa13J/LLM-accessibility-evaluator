import time

# Retrieves captured mutations from the Mutation Observer.
def extract_mutation_observer_results(driver):
    time.sleep(0.5)
    raw_mutations = driver.execute_script("return window.mutationRecords || []")

    structured_mutations = []
    for m in raw_mutations:
        structured_mutations.append({
            "type": m.get("type"),
            "target": m.get("target", ""),
            "targetTag": m.get("targetTag", ""),
            "targetId": m.get("targetId", ""),
            "targetClass": m.get("targetClass", ""),
            "attributeChanged": m.get("attributeChanged", ""),
            "newValue": m.get("newValue", ""),
            "validationFlag": m.get("validationFlag", False),
            "addedNodes": m.get("addedNodes", []),
            "removedNodes": m.get("removedNodes", []),
            "possibleErrorMessages": m.get("possibleErrorMessages", []),
            "timestamp": m.get("timestamp", None),
        })

    return structured_mutations
