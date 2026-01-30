import argparse
import csv
import json
import math
import os
from pathlib import Path

EPS = 1e-12

NUM_COLS_DEFAULT = ["SSE", "SSE_next", "improve_ratio", "a", "s", "step_norm", "cond", "err_abs", "r", "risk"]

def is_number(x):
    return isinstance(x, (int, float)) and math.isfinite(x)

def to_float(v):
    try:
        x = float(v)
        if math.isfinite(x):
            return x
        return None
    except Exception:
        return None

def read_last_row_csv(path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
        if not rows:
            return None
        return rows[-1], rows

def safe_var(xs):
    xs = [x for x in xs if x is not None and is_number(x)]
    n = len(xs)
    if n <= 1:
        return 0.0
    m = sum(xs) / n
    return sum((x - m) * (x - m) for x in xs) / (n - 1)

def norm_var(xs):
    xs2 = [x for x in xs if x is not None and is_number(x)]
    if len(xs2) <= 1:
        return 0.0
    mu = sum(abs(x) for x in xs2) / max(1, len(xs2))
    v = safe_var(xs2)
    return v / ((mu + EPS) * (mu + EPS))

def find_trace_files(root: Path, name="trace_sse.csv"):
    return sorted(root.rglob(name))

def summarize_run(rows, last_row):
    status = str(last_row.get("status", "UNKNOWN")).strip().upper()
    iters = len(rows)
    out = {
        "status": status,
        "iters": iters,
    }

    for k in ["SSE", "a", "s", "step_norm", "cond", "err_abs", "r", "risk"]:
        if k in last_row:
            out[f"final_{k}"] = to_float(last_row.get(k))

    max_cond = None
    max_step = None
    min_a = None
    max_s = None

    for r in rows:
        c = to_float(r.get("cond")) if "cond" in r else None
        sn = to_float(r.get("step_norm")) if "step_norm" in r else None
        a = to_float(r.get("a")) if "a" in r else None
        s = to_float(r.get("s")) if "s" in r else None

        if c is not None:
            max_cond = c if max_cond is None else max(max_cond, c)
        if sn is not None:
            max_step = sn if max_step is None else max(max_step, sn)
        if a is not None:
            min_a = a if min_a is None else min(min_a, a)
        if s is not None:
            max_s = s if max_s is None else max(max_s, s)

    out["max_cond"] = max_cond
    out["max_step_norm"] = max_step
    out["min_a"] = min_a
    out["max_s"] = max_s
    return out

def drift_report(run_summaries):
    finals = {}
    for k in run_summaries[0].keys():
        if k.startswith("final_") or k in ["iters", "max_cond", "max_step_norm", "min_a", "max_s"]:
            finals[k] = [rs.get(k) for rs in run_summaries]

    drift = {}
    for k, xs in finals.items():
        drift[f"D_{k}"] = norm_var(xs)

    deny_rate = sum(1 for rs in run_summaries if rs["status"] == "DENY") / max(1, len(run_summaries))
    abstain_rate = sum(1 for rs in run_summaries if rs["status"].startswith("ABSTAIN")) / max(1, len(run_summaries))

    drift["deny_rate"] = deny_rate
    drift["abstain_rate"] = abstain_rate
    return drift

def pick_top_drifts(drift, topn=5):
    items = [(k, v) for k, v in drift.items() if k.startswith("D_")]
    items.sort(key=lambda kv: kv[1], reverse=True)
    return items[:topn]

def compute_stability(drift, weights=None):
    if weights is None:
        weights = {}

    D_total = 0.0
    for k, v in drift.items():
        if not k.startswith("D_"):
            continue
        w = weights.get(k, 1.0)
        D_total += w * float(v)

    D_total += 2.0 * drift.get("deny_rate", 0.0)
    D_total += 1.0 * drift.get("abstain_rate", 0.0)

    S = 1.0 / (1.0 + D_total)
    return D_total, S

def write_csv_rows(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Root folder containing many trace_sse.csv files (recursive).")
    ap.add_argument("--trace_name", default="trace_sse.csv")
    ap.add_argument("--out_dir", default="ssd_out")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    traces = find_trace_files(root, name=args.trace_name)
    if not traces:
        raise SystemExit(f"No {args.trace_name} found under: {root}")

    run_summaries = []
    for p in traces:
        last_row, rows = read_last_row_csv(str(p))
        if last_row is None:
            continue
        rs = summarize_run(rows, last_row)
        rs["trace_path"] = str(p)
        run_summaries.append(rs)

    if not run_summaries:
        raise SystemExit("No valid traces parsed.")

    drift = drift_report(run_summaries)
    D_total, S = compute_stability(drift)

    top = pick_top_drifts(drift, topn=6)

    report = {
        "root": str(root),
        "trace_name": args.trace_name,
        "n_traces": len(run_summaries),
        "D_total": D_total,
        "S": S,
        "deny_rate": drift.get("deny_rate", 0.0),
        "abstain_rate": drift.get("abstain_rate", 0.0),
        "top_drifts": [{"name": k, "value": v} for k, v in top],
    }

    with open(out_dir / "ssd_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    keys = sorted({k for rs in run_summaries for k in rs.keys()})
    keys = [k for k in keys if k != "trace_path"] + ["trace_path"]
    rows_csv = []
    for rs in run_summaries:
        row = []
        for k in keys:
            row.append(rs.get(k))
        rows_csv.append(row)

    write_csv_rows(out_dir / "ssd_runs.csv", keys, rows_csv)

    lines = []
    lines.append("SHUNYAYA STRUCTURAL DIAGNOSIS (SSD) — TRACE DIAGNOSTIC REPORT")
    lines.append("")
    lines.append(f"root: {root}")
    lines.append(f"trace_name: {args.trace_name}")
    lines.append(f"traces: {len(run_summaries)}")
    lines.append("")
    lines.append(f"D_total: {D_total:.6g}")
    lines.append(f"S = 1 / (1 + D_total): {S:.6g}")
    lines.append(f"deny_rate: {report['deny_rate']:.6g}")
    lines.append(f"abstain_rate: {report['abstain_rate']:.6g}")
    lines.append("")
    lines.append("TOP DRIFT SOURCES:")
    for k, v in top:
        lines.append(f" - {k}: {v:.6g}")
    lines.append("")
    lines.append("OUTPUTS:")
    lines.append(f" - {out_dir / 'ssd_report.json'}")
    lines.append(f" - {out_dir / 'ssd_runs.csv'}")

    with open(out_dir / "ssd_report.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n".join(lines))

if __name__ == "__main__":
    main()
