import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import pandas as pd


def clean_url(url):
    """Extract only the domain part between www. and .com/.org/etc."""
    match = re.search(r"www\.([^.]+)\.", url)
    return match.group(1) if match else url.split("//")[-1].split("/")[0]


def clean_model(model):
    """Simplify model names to 'gpt-4' or 'gpt-5'."""
    if "gpt-4" in model.lower():
        return "gpt-4"
    elif "gpt-5" in model.lower():
        return "gpt-5"
    return model.split("/")[-1]


def evaluate_entries(entries):
    """Evaluate a list of entries for one run (same structure as before)."""
    y_true, y_pred = [], []
    flagged_cases = []
    total_fields = 0
    TP = TN = FP = FN = 0

    model_name = clean_model(entries[0].get("model", "Unknown"))
    url = clean_url(entries[0].get("url", "Unknown"))

    for entry in entries:
        for field in entry["fields"]:
            total_fields += 1
            ident = field.get("identification", "Unknown")
            gold = field.get("benchmark", "").strip().lower()
            pred = field.get("evaluation", "").strip().lower()

            # Handle benchmark N/A
            if gold == "n/a":
                if pred == "fail":
                    y_true.append(0); y_pred.append(1)  # FP
                    FP += 1
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "False violation (n/a → fail)"
                    })
                else:
                    continue

            elif gold == "fail":
                if pred == "fail":
                    y_true.append(1); y_pred.append(1)
                    TP += 1
                elif pred in ("pass", "inapplicable"):
                    y_true.append(1); y_pred.append(0)
                    FN += 1
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "Missed violation (fail → pass/inapplicable)"
                    })
                elif pred == "absent":
                    # Skip — model didn’t evaluate this field
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "No evaluation (fail → absent)"
                    })
                    continue

            elif gold == "pass":
                if pred == "fail":
                    y_true.append(0); y_pred.append(1)
                    FP += 1
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "False violation (pass → fail)"
                    })
                elif pred in ("pass", "inapplicable"):
                    y_true.append(0); y_pred.append(0)
                    TN += 1
                elif pred == "absent":
                    # Skip — model didn’t evaluate this field
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "No evaluation (pass → absent)"
                    })
                    continue

            elif gold == "inapplicable":
                if pred == "fail":
                    y_true.append(0); y_pred.append(1)
                    FP += 1
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "False violation (inapplicable → fail)"
                    })
                elif pred in ("pass", "inapplicable", "absent"):
                    # Skip — nothing to compare
                    continue

    # Compute metrics
    if y_true:
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        coverage = f"{len(y_true)}/{total_fields} ({len(y_true)/total_fields:.1%})"
    else:
        accuracy = precision = recall = f1 = 0
        coverage = f"0/{total_fields} (0%)"

    metrics = {
        "Model": model_name,
        "URL": url,
        "True Positives": TP,
        "True Negatives": TN,
        "False Positives": FP,
        "False Negatives": FN,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-score": f1,
        "Coverage": coverage,
        "Total samples used": len(y_true)
    }

    return metrics, flagged_cases



def evaluate_multi_model(results_file, output_prefix="evaluation_results"):
    with open(results_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    grouped = defaultdict(list)
    for entry in data:
        key = (clean_url(entry["url"]), clean_model(entry["model"]))
        grouped[key].append(entry)

    all_metrics = []
    consistency_tracker = defaultdict(lambda: defaultdict(list))
    field_benchmarks = defaultdict(lambda: defaultdict(str))

    for (url, model), entries in grouped.items():
        print(f"Processing {model} on {url} ({len(entries)} runs)")
        for run_id, entry in enumerate(entries, 1):
            metrics, flagged = evaluate_entries([entry])
            metrics["Run ID"] = run_id
            all_metrics.append(metrics)

            # Collect field-level predictions + benchmark
            for f in entry["fields"]:
                fid = f.get("identification", "Unknown")
                pred = f.get("evaluation", "").strip().lower()
                benchmark = f.get("benchmark", "").strip().lower()
                consistency_tracker[(url, model)][fid].append(pred)
                field_benchmarks[(url, model)][fid] = benchmark

    # Consistency summary
    consistency_summary = []
    for (url, model), field_preds in consistency_tracker.items():
        for fid, preds in field_preds.items():
            counts = Counter(preds)
            count_str = ", ".join(f"{v}×{k}" for k, v in counts.items())
            dominant = counts.most_common(1)[0]
            consistency = dominant[1] / len(preds)
            benchmark = field_benchmarks[(url, model)][fid]
            consistency_summary.append({
                "URL": url,
                "Model": model,
                "Field": fid,
                "Runs": len(preds),
                "Eval counts": count_str,
                "Most common": dominant[0],
                "Consistency ratio": round(consistency, 2),
                "Benchmark": benchmark
            })

        # Compute totals across all models and URLs
    totals = {
        "True Positives": sum(m["True Positives"] for m in all_metrics),
        "True Negatives": sum(m["True Negatives"] for m in all_metrics),
        "False Positives": sum(m["False Positives"] for m in all_metrics),
        "False Negatives": sum(m["False Negatives"] for m in all_metrics),
    }

    TP, TN, FP, FN = totals.values()
    total_samples = TP + TN + FP + FN

    totals["Accuracy"] = (TP + TN) / total_samples if total_samples else 0
    totals["Precision"] = TP / (TP + FP) if (TP + FP) else 0
    totals["Recall"] = TP / (TP + FN) if (TP + FN) else 0
    totals["F1-score"] = (
        2 * totals["Precision"] * totals["Recall"] /
        (totals["Precision"] + totals["Recall"])
        if (totals["Precision"] + totals["Recall"]) else 0
    )
    totals["Total samples used"] = total_samples
    totals["Coverage"] = "N/A"
    totals["Model"] = "ALL"
    totals["URL"] = "ALL"
    totals["Run ID"] = "TOTAL"

    # Create dataframes
    metrics_df = pd.DataFrame(all_metrics)
    metrics_df = pd.concat([metrics_df, pd.DataFrame([totals])], ignore_index=True)
    consistency_df = pd.DataFrame(consistency_summary)


    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    metrics_file = f"{output_prefix}_metrics_{timestamp}.csv"
    consistency_file = f"{output_prefix}_consistency_{timestamp}.csv"

    metrics_df.to_csv(metrics_file, index=False)
    consistency_df.to_csv(consistency_file, index=False)

    print(f"\nSaved metrics to: {metrics_file}")
    print(f"Saved consistency summary to: {consistency_file}")

    return metrics_df, consistency_df


if __name__ == "__main__":
    results_file = "results_with_benchmarks_1.4.1.json"
    metrics_df, consistency_df = evaluate_multi_model(results_file)
    print("\n=== Sample Metrics ===")
    print(metrics_df.head())
    print("\n=== Sample Consistency Summary ===")
    print(consistency_df.head())
