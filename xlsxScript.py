import json
import pandas as pd

with open("results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

rows = []
for entry in data:
    url = entry["url"]
    fields = entry["fields"]

    for i, field in enumerate(fields):
        rows.append({
            "url": url if i == 0 else "",  
            "field_id": field["identification"],
            "evaluation": field["evaluation"],
            "reasoning": field["reasoning"],
            "benchmark": field.get("benchmark", "N/A"),
            "match": field.get("match", ""),
        })

df = pd.DataFrame(rows)
df.to_excel("results.xlsx", index=False)
print("Excel file created with single URL entry per evaluation.")
