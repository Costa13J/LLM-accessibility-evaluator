import time

def extract_mutation_observer_results(driver):
    time.sleep(0.5)
    raw_mutations = driver.execute_script("return window.mutationRecords || []")
    print(raw_mutations)
    structured_mutations = []
    for m in raw_mutations:
        record = {
            "type": m.get("type"),
            "timestamp": m.get("timestamp"),
        }

        # Always keep target basics
        for key in [
            "targetTag", "targetId", "targetClass",
            "attributeChanged", "oldValue", "newValue",
            "reasonCode"
        ]:
            if key in m and m[key] not in ("", None):
                record[key] = m[key]

        # Keep field metadata if available
        for key in ["fieldLabel", "fieldName", "ariaDescribedText"]:
            if key in m and m[key]:
                record[key] = m[key]

        # Keep style diffs even if no validation flag
        if "computedColorStyles" in m and m["computedColorStyles"]:
            record["computedColorStyles"] = m["computedColorStyles"]

        # Keep error-related cues
        if m.get("errorClasses"):
            record["errorClasses"] = m["errorClasses"]

        if m.get("validationFlag", False):
            record["validationFlag"] = True

        # Added and removed nodes, also error message text 
        for list_key in ["addedNodes", "removedNodes", "possibleErrorMessages"]:
            items = m.get(list_key, [])
            if items:
                record[list_key] = items

        structured_mutations.append(record)

    return structured_mutations
