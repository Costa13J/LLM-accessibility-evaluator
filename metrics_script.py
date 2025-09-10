import json
from collections import Counter
from datetime import datetime
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def evaluate_binary_with_inapplicable(results_file):
    with open(results_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Read model name (assume consistent across entries)
    model_name = data[0].get("model", "Unknown") if data else "Unknown"

    y_true, y_pred = [], []
    flagged_cases = []
    total_fields = 0

    # Counters
    TP = TN = FP = FN = 0

    for entry in data:
        url = entry["url"]
        for field in entry["fields"]:
            total_fields += 1
            ident = field.get("identification", "Unknown")
            gold = field.get("benchmark", "").strip().lower()
            pred = field.get("evaluation", "").strip().lower()

            # Skip benchmark N/A entirely
            if gold == "n/a":
                continue

            # Benchmark is fail → expected issue
            if gold == "fail":
                if pred == "fail":
                    y_true.append(1); y_pred.append(1)  # TP
                    TP += 1
                elif pred in ("pass", "inapplicable"):
                    y_true.append(1); y_pred.append(0)  # FN
                    FN += 1
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "Missed violation (fail → pass/inapplicable)"
                    })
                elif pred == "absent":
                    y_true.append(1); y_pred.append(0)  # FN
                    FN += 1
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "Missed violation (fail → absent)"
                    })

            # Benchmark is pass → expected non-issue
            elif gold == "pass":
                if pred == "fail":
                    y_true.append(0); y_pred.append(1)  # FP
                    FP += 1
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "False violation (pass → fail)"
                    })
                elif pred in ("pass", "inapplicable", "absent"):
                    y_true.append(0); y_pred.append(0)  # TN
                    TN += 1

            # Benchmark is inapplicable
            elif gold == "inapplicable":
                if pred == "fail":
                    y_true.append(0); y_pred.append(1)  # FP
                    FP += 1
                    flagged_cases.append({
                        "url": url, "field": ident,
                        "benchmark": gold, "evaluation": pred,
                        "issue": "False violation (inapplicable → fail)"
                    })
                elif pred in ("pass", "inapplicable", "absent"):
                    # ignore in metrics (not added to confusion counts)
                    continue

    # Compute metrics
    accuracy = accuracy_score(y_true, y_pred) if y_true else 0
    precision = precision_score(y_true, y_pred, zero_division=0) if y_true else 0
    recall = recall_score(y_true, y_pred, zero_division=0) if y_true else 0
    f1 = f1_score(y_true, y_pred, zero_division=0) if y_true else 0
    coverage = f"{len(y_true)}/{total_fields} ({len(y_true)/total_fields:.1%})" if total_fields else "0/0"

    # Per-class prediction breakdown
    pred_counts = Counter(y_pred)
    gold_counts = Counter(y_true)

    metrics = {
        "Model": model_name,
        "True Positives": TP,
        "True Negatives": TN,
        "False Positives": FP,
        "False Negatives": FN,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1-score": f1,
        "Coverage": coverage,
        "Total samples used": len(y_true),

        "Pred counts": dict(pred_counts),
        "Gold counts": dict(gold_counts),
    }


    """ Each field has:
            benchmark (gold label)
            evaluation (model prediction)
Gold/pred can be: "pass", "fail", "inapplicable", "absent", or "n/a".

benchmark == "n/a" → skipped (not counted at all).
benchmark == "inapplicable":
    -If prediction is "fail" → false positive (wrong).
    -If prediction is "pass", "inapplicable", or "absent" → ignored (not added to metrics at all).

So: only gold "fail" or "pass" contribute to y_true/y_pred metrics.
Gold "inapplicable" only contributes if the model wrongly predicts "fail".

Gold "fail" → y_true = 1 (expected violation).
Gold "pass" → y_true = 0 (expected no violation).
Pred "fail" → y_pred = 1.
Pred "pass", "inapplicable", "absent" → y_pred = 0.

This converts the task to binary classification (issue vs. no issue).

TP (true positive): gold fail, pred fail → the model correctly identified a real violation (benchmark = fail, prediction = fail).
FN (false negative): gold fail, pred pass/inapplicable/absent → the model claimed there was a violation, but the benchmark said there wasn’t (benchmark = pass or inapplicable, prediction = fail).
TN (true negative): gold pass, pred pass/inapplicable/absent → the model correctly identified that there was no violation (benchmark = pass, prediction = pass/inapplicable/absent).
FP (false positive): gold pass or inapplicable, pred fail → the model missed a real violation (benchmark = fail, prediction = pass/inapplicable/absent).

Metrics calculated:

Accuracy: (TP + TN) / total_used
Precision: TP / (TP + FP)
Recall: TP / (TP + FN)
F1: 2 * (Precision * Recall) / (Precision + Recall)
Coverage: fraction of fields actually evaluated out of all fields (skips "n/a" and most "inapplicable").
flagged_cases: detailed list of mismatche
"""

    # Issue type frequencies
    issue_summary = Counter([case["issue"] for case in flagged_cases])

    return metrics, flagged_cases, issue_summary


if __name__ == "__main__":
    results_file = "results_with_benchmarks_3.3.3.json"
    metrics, flagged_cases, issue_summary = evaluate_binary_with_inapplicable(results_file)

    print("=== Evaluation Report ===")
    for k, v in metrics.items():
        if isinstance(v, float):
            print(f"{k}: {v:.3f}")
        else:
            print(f"{k}: {v}")

    if issue_summary:
        print("\n=== Most Common Issues ===")
        for issue, count in issue_summary.most_common():
            print(f"- {issue}: {count}")

    if flagged_cases:
        print("\n=== Flagged Cases (examples) ===")
        for case in flagged_cases[:10]:  # limit print to first 10
            print(f"- URL: {case['url']} | Field: {case['field']} | "
                  f"Benchmark: {case['benchmark']} | Eval: {case['evaluation']} | Issue: {case['issue']}")
