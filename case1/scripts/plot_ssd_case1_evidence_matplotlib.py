#!/usr/bin/env python3
"""
Case 1 Matplotlib Evidence Plot (SSD)
Evidence-only: reads ssd_report.json and plots top drift contributors.
- No solver inputs or datasets are read.
- No SSD recomputation occurs.
- Deterministic given identical report JSON.

Polish:
- Zero/near-zero contributors are de-emphasized (gray + hatch).
- A run timestamp (UTC) is embedded in the image (top-right).
"""

import argparse
import json
import math
from pathlib import Path
from datetime import datetime, timezone

import matplotlib.pyplot as plt


def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def _fmt(x, nd=6):
    if x is None:
        return "NA"
    try:
        xf = float(x)
    except Exception:
        return "NA"
    if math.isfinite(xf) is False:
        return "NA"
    if abs(xf) >= 100:
        return f"{xf:.3f}"
    if abs(xf) >= 1:
        s = f"{xf:.6f}"
        return s.rstrip("0").rstrip(".")
    if abs(xf) == 0:
        return "0"
    return f"{xf:.6g}"


def _as_pairs(top):
    """
    Accept:
    - dict: {"name": value}
    - list of dicts: [{"name":..., "value":...}, ...]
    - list of pairs: [("name", value), ...]
    """
    if top is None:
        return []
    if isinstance(top, dict):
        out = []
        for k, v in top.items():
            out.append((str(k), _safe_float(v, 0.0)))
        return out
    if isinstance(top, list):
        out = []
        for item in top:
            if isinstance(item, (list, tuple)) and len(item) >= 2:
                out.append((str(item[0]), _safe_float(item[1], 0.0)))
            elif isinstance(item, dict):
                if "name" in item and "value" in item:
                    out.append((str(item["name"]), _safe_float(item["value"], 0.0)))
                elif "key" in item and "value" in item:
                    out.append((str(item["key"]), _safe_float(item["value"], 0.0)))
        return out
    return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, help="Path to ssd_report.json")
    ap.add_argument("--top_k", type=int, default=6, help="Number of drift sources to show")
    ap.add_argument("--title", default="SSD Evidence Snapshot (Case 1 - MGH17)")
    ap.add_argument("--out_png", required=True, help="Output PNG path")
    ap.add_argument("--epsilon", type=float, default=1e-12,
                    help="Values <= epsilon are treated as zero for display de-emphasis")
    args = ap.parse_args()

    report_path = Path(args.report)
    if not report_path.exists():
        raise FileNotFoundError(f"Report not found: {report_path}")

    with report_path.open("r", encoding="utf-8") as f:
        r = json.load(f)

    # Metrics (support common keys)
    traces = r.get("n_traces", r.get("traces", None))
    d_total = r.get("D_total", r.get("d_total", None))
    s_score = r.get("S", r.get("s_score", None))
    deny_rate = r.get("deny_rate", None)
    abstain_rate = r.get("abstain_rate", None)

    top = (
        r.get("top_drifts")
        or r.get("top_drift_sources")
        or r.get("top_sources")
        or r.get("top_drift")
        or r.get("top_drift_metrics")
        or r.get("top")
    )

    pairs = _as_pairs(top)
    pairs = [(k, v) for (k, v) in pairs if isinstance(k, str)]
    pairs.sort(key=lambda kv: kv[1], reverse=True)
    pairs = pairs[: max(1, int(args.top_k))]

    names = [k for k, _ in pairs]
    vals = [float(v) for _, v in pairs]

    # Sort for horizontal bar chart (largest at top)
    names_rev = list(reversed(names))
    vals_rev = list(reversed(vals))

    # Compute display styles: de-emphasize ~0 bars
    eps = float(args.epsilon)
    is_zero = [abs(v) <= eps for v in vals_rev]

    fig = plt.figure(figsize=(16, 8))
    ax = plt.gca()

    # Bars (default style for non-zero)
    y = list(range(len(names_rev)))
    bars = ax.barh(y, vals_rev)

    # Apply de-emphasis styling for zero-ish bars
    for b, z in zip(bars, is_zero):
        if z:
            b.set_alpha(0.35)
            b.set_hatch("//")
            # Keep default color; alpha+hatch is enough and avoids hardcoding palettes

    ax.set_yticks(y)
    ax.set_yticklabels(names_rev)
    ax.set_xlabel("Drift contribution (higher = more drift)")
    ax.set_title(args.title)

    # Top-line summary (left)
    summary = (
        f"traces={_fmt(traces)}    "
        f"D_total={_fmt(d_total)}    "
        f"S={_fmt(s_score)}    "
        f"deny_rate={_fmt(deny_rate)}    "
        f"abstain_rate={_fmt(abstain_rate)}"
    )
    fig.text(0.01, 0.985, summary, ha="left", va="top", fontsize=12)

    # Embedded run timestamp (right) — ensures each run is visibly distinct
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    fig.text(0.99, 0.985, f"run_utc={ts}", ha="right", va="top", fontsize=10)

    # Footer note (evidence-only discipline)
    foot = (
        "Note: Evidence-only plot from ssd_report.json. "
        "No solver inputs or datasets are read; no SSD recomputation occurs."
    )
    fig.text(0.01, 0.02, foot, ha="left", va="bottom", fontsize=11)

    # Make room for header/footer text
    plt.tight_layout(rect=[0.0, 0.06, 1.0, 0.93])

    out_png = Path(args.out_png)
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=200)
    plt.close(fig)

    print("Matplotlib evidence PNG written:")
    print(str(out_png.resolve()))


if __name__ == "__main__":
    main()
