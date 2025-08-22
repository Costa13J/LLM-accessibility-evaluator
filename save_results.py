import json
import os
import re


def save_to_json(prediction, url, submit_clicked, model="openai/gpt-4o", evaluation_mode="wcag-3.3.1"):
    filename = f"results_{evaluation_mode}.json"
    structured_fields = []

    def parse_format(format_str):
        field_blocks = re.split(r"-Identification.*?:", format_str)[1:]
        fields = []
        for block in field_blocks:
            try:
                identification_match = re.search(r"^(.*?)\n", block.strip())
                evaluation_match = re.search(r"-Evaluation:\s*(.*?)\n", block)
                reasoning_match = re.search(r"-Reasoning.*?:\s*(.*)", block, re.DOTALL)

                field_info = {
                    "identification": identification_match.group(1).strip() if identification_match else "Unknown",
                    "evaluation": evaluation_match.group(1).strip() if evaluation_match else "Unknown",
                    "reasoning": reasoning_match.group(1).strip() if reasoning_match else "No reasoning provided"
                }

                fields.append(field_info)
            except Exception as e:
                print(f"Error parsing block: {e}\n{block}")
        return fields

    # --- CASE 1: dual-submit (empty + invalid) ---
    if isinstance(prediction, dict) and "empty_submit" in prediction and "invalid_input_submit" in prediction:
        empty_fields = parse_format(prediction["empty_submit"].format)
        for f in empty_fields:
            f["source"] = "empty_submit"

        invalid_fields = parse_format(prediction["invalid_input_submit"].format)
        for f in invalid_fields:
            f["source"] = "invalid_input_submit"

        # Merge by identification
        merged = {}
        for f in empty_fields + invalid_fields:
            ident = f["identification"]
            if ident not in merged:
                merged[ident] = {
                    "identification": ident,
                    "empty_submit_evaluation": "N/A",
                    "invalid_input_submit_evaluation": "N/A",
                    "reasonings": []
                }

            if f["source"] == "empty_submit":
                merged[ident]["empty_submit_evaluation"] = f.get("evaluation", "Unknown")
            else:
                merged[ident]["invalid_input_submit_evaluation"] = f.get("evaluation", "Unknown")

            merged[ident]["reasonings"].append(f["reasoning"] + f" (from {f['source']})")

        structured_fields = [
            {
                "identification": ident,
                "empty_submit_evaluation": data["empty_submit_evaluation"],
                "invalid_input_submit_evaluation": data["invalid_input_submit_evaluation"],
                "reasoning": " | ".join(data["reasonings"])
            }
            for ident, data in merged.items()
        ]

    # --- CASE 2: single-submit (legacy) ---
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
