#!/usr/bin/env python3
"""
process_consistency_results.py

- Recursively finds evaluation_results_consistency_*.csv files under the two model folders.
- Parses the "Eval counts" column into numeric columns (pass_count, fail_count, inapplicable_count, absent_count, etc).
- Saves per-file processed CSVs (suffix _processed.csv).
- Produces summary CSVs per (model, issue) containing per-page and overall metrics:
    - mean_accuracy (average per-field accuracy)
    - std_accuracy (std dev of per-field accuracies)
    - consistency_rate (fraction of fields with identical predictions across all runs)
Usage:
    python process_consistency_results.py --base-dir "/path/to/parent"
If you run it from the same directory that contains the two model folders, you can omit --base-dir.
"""
import argparse
import re
import os
from pathlib import Path
import pandas as pd
import numpy as np
from collections import defaultdict

# -----------------------
# Configuration / safety
# -----------------------
# Default base directory (current dir). Change when calling the script.
DEFAULT_BASE_DIR = "."

# If True, writes processed files with suffix _processed.csv (recommended).
# If you prefer to overwrite originals, set overwrite_original=True below.
save_processed = True
overwrite_original = False

# Where to write aggregate summaries
SUMMARIES_DIRNAME = "summaries"

# Regex to extract patterns like: "3×pass", "10×pass", "3 x pass", "3× pass", "3xpass", "3×pass, 7×absent"
# Also handles encoding artifacts like "Ã—" (we normalize before parsing)
COUNT_LABEL_RE = re.compile(r"(\d+)\s*[×xX\u00d7\u00e7]?\s*[,]?\s*([A-Za-z0-9_\-\/\s\(\)]+)", flags=re.UNICODE)

# known labels normalization map
LABEL_NORMALIZATION = {
    "pass": "pass",
    "fail": "fail",
    "inapplicable": "inapplicable",
    "absent": "absent",
    "n/a": "n/a",
    "na": "n/a",
    "not applicable": "n/a"
}

def normalize_label(raw_label: str) -> str:
    lab = raw_label.strip().lower()
    # remove surrounding punctuation and spaces
    lab = re.sub(r"^[^\w]+|[^\w]+$", "", lab)
    # normalize common forms
    if lab in LABEL_NORMALIZATION:
        return LABEL_NORMALIZATION[lab]
    # if contains 'inapplicable'
    if "inapplic" in lab:
        return "inapplicable"
    if lab in ("n/a", "na", "notapplicable"):
        return "n/a"
    return lab

def parse_eval_counts(cell: str) -> dict:
    """
    Parse a string like:
      "3×pass, 7×absent"
      "10×pass"
      "3×pass, 4×fail, 3×inapplicable"
    Return a dict {label: int}
    """
    counts = defaultdict(int)
    if pd.isna(cell):
        return counts
    s = str(cell)
    # fix encoding artifacts that often appear as Ã— for ×
    s = s.replace("Ã—", "×")
    s = s.replace("×", "×")  # keep it; regex handles '×' and 'x'
    # Replace other odd separators
    s = s.replace(";", ",")
    # Try to find pairs of number + label
    # First: split by commas and ' / ' and ' ; '
    parts = re.split(r"[,\|/]+", s)
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # try to find number and label with regex
        m = re.search(r"(\d+)\s*[×xX\u00d7]?\s*([A-Za-z0-9_\-\/\s\(\)]+)", p)
        if m:
            n = int(m.group(1))
            lab = normalize_label(m.group(2))
            counts[lab] += n
        else:
            # fallback: maybe it's "10pass" or "pass" or "absent"
            m2 = re.search(r"(\d+)", p)
            if m2:
                # number present but no label -> ambiguous, store as unknown_{i}
                n = int(m2.group(1))
                rest = re.sub(r"\d+", "", p).strip()
                lab = normalize_label(rest) if rest else "unknown"
                counts[lab] += n
            else:
                # no number: maybe it's a single label (means 1)
                lab = normalize_label(p)
                counts[lab] += 1
    return dict(counts)

def compute_field_accuracy(counts: dict, runs: int, benchmark_raw: str) -> float:
    """
    Accuracy per field = (count of runs predicting the benchmark) / runs
    Special: If benchmark is 'inapplicable' or 'n/a', treat 'inapplicable' or 'n/a' predictions as matching.
    """
    if runs == 0:
        return np.nan
    if pd.isna(benchmark_raw):
        benchmark = None
    else:
        benchmark = str(benchmark_raw).strip().lower()
    # normalize
    if benchmark in ("n/a", "na", "not applicable"):
        benchmark_norm = "n/a"
    elif benchmark in ("inapplicable",):
        benchmark_norm = "inapplicable"
    else:
        benchmark_norm = benchmark

    correct_count = 0
    if benchmark_norm in (None, ""):
        # no benchmark -> treat as NaN for accuracy
        return np.nan

    # If benchmark is inapplicable or n/a, accept either 'inapplicable' or 'n/a'
    if benchmark_norm in ("inapplicable", "n/a"):
        correct_count = counts.get("inapplicable", 0) + counts.get("n/a", 0)
    else:
        correct_count = counts.get(benchmark_norm, 0)

    # safety: bound
    correct_count = min(correct_count, runs)
    return correct_count / runs

def is_consistent(counts: dict, runs: int) -> bool:
    if runs == 0:
        return False
    if not counts:
        return False
    max_count = max(counts.values())
    return max_count == runs

# -------------------------
# Main processing function
# -------------------------
def process_all(base_dir: str):
    base = Path(base_dir).resolve()
    # models folders - look for folders inside base dir that match the names provided:
    # but we'll just search recursively for CSV files of that naming pattern.
    csv_pattern = "**/evaluation_results_consistency_*.csv"

    processed_files = []
    summaries = defaultdict(lambda: defaultdict(lambda: {"per_page": {}, "all_fields": []}))
    # key structure: summaries[model][issue] -> dict with per_page metrics and list of field-level entries

    for csv_path in base.glob(csv_pattern):
        try:
            df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"Skipping {csv_path}: couldn't read CSV ({e})")
            continue

        # try to infer model & issue & page from path: expecting something like
        # .../resultados novos 4o/clarity/page_1/evaluation_results_consistency_...
        parts = csv_path.parts
        # naive search for known top-level folders
        model = None
        issue = None
        page = None
        # find model folder name as one of the two that you specified
        for p in parts:
            if p.lower().startswith("resultados novos 4o"):
                model = "gpt-4o"
            if p.lower().startswith("resultados novos 5"):
                model = "gpt-5"
        # find issue as one of the known issues
        for known_issue in ("clarity", "color", "identification", "required"):
            if known_issue in [pp.lower() for pp in parts]:
                issue = known_issue
                break
        # page is the immediate folder under issue (find index of issue and take next part if exists)
        if issue:
            try:
                i = [pp.lower() for pp in parts].index(issue)
                if i + 1 < len(parts) - 1:  # not the CSV itself
                    page = parts[i + 1]
                else:
                    page = "unknown_page"
            except ValueError:
                page = "unknown_page"
        else:
            page = "unknown_page"

        # Ensure expected columns exist
        if "Eval counts" not in df.columns:
            print(f"Skipping {csv_path}: 'Eval counts' column not found.")
            continue

        # parse Eval counts into numeric columns
        parsed_counts_list = []
        all_labels_found = set()
        for cell in df["Eval counts"]:
            counts = parse_eval_counts(cell)
            parsed_counts_list.append(counts)
            all_labels_found.update(counts.keys())

        # ensure columns for known labels
        label_cols = sorted(list(all_labels_found))
        # build new dataframe columns with counts (0 if missing)
        counts_df = pd.DataFrame([
            {lab + "_count": counts.get(lab, 0) for lab in label_cols}
            for counts in parsed_counts_list
        ])

        # join counts_df with original
        df_proc = df.copy()
        # drop original Eval counts column (user asked to replace)
        df_proc = df_proc.drop(columns=["Eval counts"])
        # add counts columns
        df_proc = pd.concat([df_proc.reset_index(drop=True), counts_df.reset_index(drop=True)], axis=1)

        # Add computed fields: runs (use existing Runs column if present), computed_accuracy, consistent_flag
        if "Runs" in df_proc.columns:
            runs_series = df_proc["Runs"].fillna(0).astype(int)
        else:
            # try to infer runs as sum of counts
            runs_series = counts_df.sum(axis=1).astype(int)

        df_proc["Runs"] = runs_series

        # reconstruct counts dict per row for accuracy and consistency computations
        field_counts_dicts = []
        accuracies = []
        consistent_flags = []
        for idx, row in df_proc.iterrows():
            counts = {lab: int(row.get(lab + "_count", 0)) for lab in label_cols}
            field_counts_dicts.append(counts)
            runs = int(row["Runs"]) if not pd.isna(row["Runs"]) else 0
            bench = row.get("Benchmark", "")
            acc = compute_field_accuracy(counts, runs, bench)
            accuracies.append(acc)
            consistent_flags.append(is_consistent(counts, runs))

        df_proc["field_accuracy"] = accuracies
        df_proc["is_consistent"] = consistent_flags

        # Save processed CSV
        if save_processed:
            out_path = csv_path.with_name(csv_path.stem + "_processed.csv")
            if overwrite_original:
                out_path = csv_path
            df_proc.to_csv(out_path, index=False)
            processed_files.append(out_path)
            print(f"Wrote processed file: {out_path}")
        else:
            print(f"Processed (not saved) {csv_path}")

        # Add to summaries structure
        model_key = model or "unknown_model"
        issue_key = issue or "unknown_issue"
        # compute per-page aggregated stats (over fields in this CSV)
        per_field_accuracies = [a for a in accuracies if not pd.isna(a)]
        if per_field_accuracies:
            mean_acc = float(np.mean(per_field_accuracies))
            std_acc = float(np.std(per_field_accuracies, ddof=0))
        else:
            mean_acc = float("nan")
            std_acc = float("nan")
        consistency_rate = float(sum(1 for x in consistent_flags if x) / max(1, len(consistent_flags)))

        summaries[model_key][issue_key]["per_page"][page] = {
            "n_fields": len(df_proc),
            "mean_accuracy": mean_acc,
            "std_accuracy": std_acc,
            "consistency_rate": consistency_rate
        }

        # store field-level entries for overall aggregation
        # we'll store dicts with page, field, accuracy, is_consistent
        for idx, row in df_proc.iterrows():
            summaries[model_key][issue_key]["all_fields"].append({
                "page": page,
                "URL": row.get("URL", ""),
                "Field": row.get("Field", ""),
                "Runs": int(row.get("Runs", 0)) if not pd.isna(row.get("Runs", 0)) else 0,
                "benchmark": row.get("Benchmark", ""),
                "field_accuracy": row.get("field_accuracy", np.nan),
                "is_consistent": bool(row.get("is_consistent", False))
            })

    # After processing all files, write summary CSVs
    summaries_dir = Path(base / SUMMARIES_DIRNAME)
    summaries_dir.mkdir(parents=True, exist_ok=True)

    for model_key, issues_map in summaries.items():
        for issue_key, payload in issues_map.items():
            per_page = payload["per_page"]
            all_fields = payload["all_fields"]
            # per-page summary frame
            per_page_rows = []
            for page_name, stats in per_page.items():
                per_page_rows.append({
                    "page": page_name,
                    "n_fields": stats["n_fields"],
                    "mean_accuracy": stats["mean_accuracy"],
                    "std_accuracy": stats["std_accuracy"],
                    "consistency_rate": stats["consistency_rate"]
                })
            per_page_df = pd.DataFrame(per_page_rows).sort_values(by="page")

            # overall metrics across all fields
            af_df = pd.DataFrame(all_fields)
            valid_acc = af_df["field_accuracy"].dropna()
            overall_mean_acc = float(valid_acc.mean()) if not valid_acc.empty else float("nan")
            overall_std_acc = float(valid_acc.std(ddof=0)) if not valid_acc.empty else float("nan")
            overall_consistency_rate = float(af_df["is_consistent"].sum() / max(1, len(af_df)))

            # write per-page summary CSV
            per_page_out = summaries_dir / f"{model_key}_{issue_key}_per_page_summary.csv"
            per_page_df.to_csv(per_page_out, index=False)
            # write overall summary (single-row)
            overall_out = summaries_dir / f"{model_key}_{issue_key}_overall_summary.csv"
            overall_summary = pd.DataFrame([{
                "model": model_key,
                "issue": issue_key,
                "n_pages": len(per_page_df),
                "n_fields_total": len(af_df),
                "mean_accuracy": overall_mean_acc,
                "std_accuracy": overall_std_acc,
                "consistency_rate": overall_consistency_rate
            }])
            overall_summary.to_csv(overall_out, index=False)

            # also save the full field-level table for reference
            field_level_out = summaries_dir / f"{model_key}_{issue_key}_fields.csv"
            af_df.to_csv(field_level_out, index=False)

            print(f"Wrote summaries for {model_key} / {issue_key}:")
            print(f"  per-page -> {per_page_out}")
            print(f"  overall -> {overall_out}")
            print(f"  field-level -> {field_level_out}")

    print("Processing complete.")
    print(f"Processed files: {len(processed_files)}")
    print(f"Summaries written to: {summaries_dir}")

# -------------------------
# CLI entrypoint
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process evaluation_results_consistency CSVs.")
    parser.add_argument("--base-dir", "-b", default=DEFAULT_BASE_DIR, help="Base directory containing the model folders (default: current dir)")
    args = parser.parse_args()
    process_all(args.base_dir)
