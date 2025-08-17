import time

# Retrieves and filters captured mutations from the Mutation Observer
def extract_mutation_observer_results(driver):
    time.sleep(0.5)
    raw_mutations = driver.execute_script("return window.mutationRecords || []")

    structured_mutations = []
    for m in raw_mutations:
        record = {
            "type": m.get("type"),
            "timestamp": m.get("timestamp"),
        }

        # Add only non-empty fields
        for key in [
            "target", "targetTag", "targetId", "targetClass",
            "attributeChanged", "newValue", "ariaDescribedText", "reasonCode",
            "computedColorStyles", "colorProperties", "errorClasses",
            "fieldLabel", "fieldName"
        ]:
            value = m.get(key, "")
            if value:
                record[key] = value

        # Only include validation flag if true
        if m.get("validationFlag", False):
            record["validationFlag"] = True

        # Only include added/removed nodes or error messages if not empty
        for list_key in ["addedNodes", "removedNodes", "possibleErrorMessages"]:
            items = m.get(list_key, [])
            if items:
                record[list_key] = items

        structured_mutations.append(record)

    return structured_mutations
