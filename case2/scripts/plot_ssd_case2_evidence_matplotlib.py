#!/usr/bin/env python3

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


def _fmt(x):
    if x is None:
        return "NA"
    try:
        xf = float(x)
    except Exception:
        return "NA"
    if not math.isfinite(xf):
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
    if top is None:
        return []
    if isinstance(top, dict):
        return [(str(k), _safe_float(v, 0.0)) for k, v in top.items()]
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
    ap.add_argument("--top_k", type=int, default=6)
    ap.add_argument("--title", required=True)
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--out_png", required=True)
    ap.add_argument("--epsilon", type=float, default=1e-12)
    args = ap.parse_args()

    rp = Path(args.report)
    if not rp.exists():
        raise FileNotFoundError(str(rp))

    with rp.open("r", encoding="utf-8") as f:
        r = json.load(f)

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

    names = list(reversed(names))
    vals = list(reversed(vals))

    eps = float(args.epsilon)
    zeroish = [abs(v) <= eps for v in vals]

    fig = plt.figure(figsize=(16, 8))
    ax = plt.gca()

    y = list(range(len(names)))
    bars = ax.barh(y, vals)

    for b, z in zip(bars, zeroish):
        if z:
            b.set_alpha(0.35)
            b.set_hatch("//")

    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.set_xlabel("Drift contribution (higher = more drift)")

    if args.subtitle.strip():
        ax.set_title(args.title + "\n" + args.subtitle)
    else:
        ax.set_title(args.title)

    summary = (
        f"traces={_fmt(traces)}    "
        f"D_total={_fmt(d_total)}    "
        f"S={_fmt(s_score)}    "
        f"deny_rate={_fmt(deny_rate)}    "
        f"abstain_rate={_fmt(abstain_rate)}"
    )
    fig.text(0.01, 0.985, summary, ha="left", va="top", fontsize=12)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%SZ")
    fig.text(0.99, 0.985, f"run_utc={ts}", ha="right", va="top", fontsize=10)

    foot = "Evidence-only plot from ssd_report.json. No trace generation and no SSD recomputation."
    fig.text(0.01, 0.02, foot, ha="left", va="bottom", fontsize=11)

    plt.tight_layout(rect=[0.0, 0.06, 1.0, 0.93])

    outp = Path(args.out_png)
    outp.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(outp, dpi=200)
    plt.close(fig)

    print("Matplotlib evidence PNG written:")
    print(str(outp.resolve()))


if __name__ == "__main__":
    main()
