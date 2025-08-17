import json
import os
import re


def save_to_json(prediction, url, submit_clicked, model, evaluation_mode="wcag-3.3.1"):
    filename = f"results_{evaluation_mode}.json"
    structured_fields = []

    def parse_format(format_str):
        field_blocks = re.split(r"-Identification\(label or name of the field\):", format_str)[1:]
        fields = []
        for block in field_blocks:
            try:
                lines = block.strip().split("\n")
                identification = lines[0].strip()
                required_eval = re.search(r'-Required Cue Evaluation\("?(.*?)"?\)', block)
                error_eval = re.search(r'-Error Cue Evaluation\("?(.*?)"?\)', block)
                reasoning_match = re.search(r'-Reasoning\(.*?\):\s*(.*)', block, re.DOTALL)

                field_info = {
                    "identification": identification,
                    "required_evaluation": required_eval.group(1).strip() if required_eval else "Unknown",
                    "error_evaluation": error_eval.group(1).strip() if error_eval else "Unknown",
                    "reasoning": reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
                }

                fields.append(field_info)
            except Exception as e:
                print(f"Error parsing block: {e}\n{block}")
        return fields

    if isinstance(prediction, dict) and "empty_submit" in prediction and "invalid_input_submit" in prediction:
        empty_fields = parse_format(prediction["empty_submit"].format)
        for f in empty_fields:
            f["source"] = "empty_submit"
            # Kept the full evaluation here as both required and error are meaningful on empty submission

        invalid_fields = parse_format(prediction["invalid_input_submit"].format)
        for f in invalid_fields:
            f["source"] = "invalid_input_submit"
            # For invalid inputs, required cues are redundant
            f.pop("required_evaluation", None)

        structured_fields = empty_fields + invalid_fields

    else:
        structured_fields = parse_format(prediction.format)


    result_entry = {
        "url": url,
        "model": model,
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
