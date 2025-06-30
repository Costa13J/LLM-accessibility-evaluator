import json
from collections import defaultdict

with open("results_with_benchmarks_required.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Group entries by URL
grouped_by_url = defaultdict(list)
for entry in data:
    grouped_by_url[entry["url"]].append(entry)

grand_matched = 0
grand_total = 0
grand_reasoning_mismatches = 0

for url, runs in grouped_by_url.items():
    matched = 0
    total_relevant = 0
    reasoning_mismatches = 0

    for run in runs:
        for field in run["fields"]:
            match = field.get("match")
            benchmark = field.get("benchmark", "").strip().lower()
            evaluation = field.get("evaluation", "").strip().lower()

            if field.get("reasoning_mismatch", False):
                reasoning_mismatches += 1

            if match == "✅":
                matched += 1
                total_relevant += 1
            elif match == "❌":
                total_relevant += 1
            elif match == "absent":
                if benchmark == "fail":
                    total_relevant += 1  # counts as mismatch
            elif benchmark == "n/a":
                # Only counts as mismatch if NOT 'inapplicable' AND NOT 'pass'
                if evaluation not in ["inapplicable", "pass"]:
                    total_relevant += 1

    grand_matched += matched
    grand_total += total_relevant
    grand_reasoning_mismatches += reasoning_mismatches

    accuracy = matched / total_relevant if total_relevant > 0 else 0
    print(f"{url}: {accuracy:.2%} ({matched}/{total_relevant} correct), Reasoning mismatches: {reasoning_mismatches}")

overall_accuracy = grand_matched / grand_total if grand_total > 0 else 0
print(f"\nOverall Accuracy: {overall_accuracy:.2%} ({grand_matched}/{grand_total} correct)")
print(f"Total Reasoning Mismatches: {grand_reasoning_mismatches}")
