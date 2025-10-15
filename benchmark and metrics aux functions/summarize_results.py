import json
from collections import defaultdict

with open("results_with_benchmarks_3.3.3.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Group entries by URL
grouped_by_url = defaultdict(list)
for entry in data:
    grouped_by_url[entry["url"]].append(entry)

# Grand totals for accuracy report
grand_matched = 0
grand_total = 0
grand_reasoning_mismatches = 0

# Totals for full summary
total_fields = 0
match_counts = {"✅": 0, "❌": 0, "absent": 0}
n_a_cases = 0
reasoning_mismatches = 0

# === Per-URL Accuracy Summary ===
print("=== Accuracy Per URL ===")
for url, runs in grouped_by_url.items():
    matched = 0
    total_relevant = 0
    reasoning_mismatches_url = 0

    for run in runs:
        for field in run["fields"]:
            match = field.get("match")
            benchmark = field.get("benchmark", "").strip().lower()
            evaluation = field.get("evaluation", "").strip().lower()

            if field.get("reasoning_mismatch", False):
                reasoning_mismatches_url += 1

            if match == "✅":
                matched += 1
                total_relevant += 1
            elif match == "❌":
                total_relevant += 1
            elif match == "absent":
                if benchmark == "fail":
                    total_relevant += 1
            elif benchmark == "n/a":
                if evaluation not in ["inapplicable", "pass"]:
                    total_relevant += 1

            # Full summary tracking
            total_fields += 1
            if match in match_counts:
                match_counts[match] += 1
            if benchmark == "n/a":
                n_a_cases += 1
            if field.get("reasoning_mismatch", False):
                reasoning_mismatches += 1

    grand_matched += matched
    grand_total += total_relevant
    grand_reasoning_mismatches += reasoning_mismatches_url

    accuracy = matched / total_relevant if total_relevant > 0 else 0
    print(f"{url}: {accuracy:.2%} ({matched}/{total_relevant} correct), Reasoning mismatches: {reasoning_mismatches_url}")

# === Overall Accuracy Summary ===
overall_accuracy = grand_matched / grand_total if grand_total > 0 else 0
print(f"\nOverall Accuracy: {overall_accuracy:.2%} ({grand_matched}/{grand_total} correct)")
print(f"Total Reasoning Mismatches: {grand_reasoning_mismatches}")

# === Full Field-Level Summary ===
print("\n=== Full Summary of All Evaluated Fields ===")
print(f"Total Fields Evaluated: {total_fields}")
print(f"✅ Matches: {match_counts['✅']} ({match_counts['✅']/total_fields:.2%})")
print(f"❌ Mismatches: {match_counts['❌']} ({match_counts['❌']/total_fields:.2%})")
print(f"Absent Matches: {match_counts['absent']} ({match_counts['absent']/total_fields:.2%})")
print(f"Benchmarked as N/A: {n_a_cases} ({n_a_cases/total_fields:.2%})")
print(f"Reasoning mismatches: {reasoning_mismatches} ({reasoning_mismatches/total_fields:.2%})")
