import json
from collections import defaultdict

with open("results_with_benchmarks_required.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Group entries by URL
grouped_by_url = defaultdict(list)
for entry in data:
    grouped_by_url[entry["url"]].append(entry)

# Counters
total_fields = 0
match_counts = {"✅": 0, "❌": 0, "absent": 0}
n_a_cases = 0
reasoning_mismatches = 0

# Loop through all fields
for runs in grouped_by_url.values():
    for run in runs:
        for field in run["fields"]:
            match = field.get("match")
            benchmark = field.get("benchmark", "").strip().lower()
            evaluation = field.get("evaluation", "").strip().lower()
            reason_mismatch = field.get("reasoning_mismatch", False)

            total_fields += 1
            if match in match_counts:
                match_counts[match] += 1
            if benchmark == "n/a":
                n_a_cases += 1
            if reason_mismatch:
                reasoning_mismatches += 1

# Summary
print("=== Full Summary of All Evaluated Fields ===")
print(f"Total Fields Evaluated: {total_fields}")
print(f"✅ Matches: {match_counts['✅']} ({match_counts['✅']/total_fields:.2%})")
print(f"❌ Mismatches: {match_counts['❌']} ({match_counts['❌']/total_fields:.2%})")
print(f"Absent Matches: {match_counts['absent']} ({match_counts['absent']/total_fields:.2%})")
print(f"Benchmarked as N/A: {n_a_cases} ({n_a_cases/total_fields:.2%})")
print(f"Reasoning mismatches: {reasoning_mismatches} ({reasoning_mismatches/total_fields:.2%})")
