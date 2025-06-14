import json
import os
import re


def save_to_json(prediction, url, submit_clicked, filename="results.json"):
    field_blocks = re.split(r"-Identification:", prediction.format)[1:]
    structured_fields = []

    for block in field_blocks:
        try:
            identification_match = re.search(r"^(.*?)\n", block.strip())
            evaluation_match = re.search(r"-Evaluation:\s*(.*?)\n", block)
            reasoning_match = re.search(r"-Reasoning:\s*(.*)", block, re.DOTALL)

            field_info = {
                "identification": identification_match.group(1).strip() if identification_match else "Unknown",
                "evaluation": evaluation_match.group(1).strip() if evaluation_match else "Unknown",
                "reasoning": reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
            }

            structured_fields.append(field_info)
        except Exception as e:
            print(f"Error parsing block: {e}\n{block}")

    result_entry = {
        "url": url,
        "submit_clicked": submit_clicked,
        "fields": structured_fields
    }

    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = []

        existing_data.append(result_entry)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, indent=4, ensure_ascii=False)
        print(f"Structured results saved to {filename}")
    except Exception as e:
        print(f"Error saving results: {e}")