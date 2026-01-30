# plot_ssd_case1_evidence_svg.py
import argparse
import json
import math
from pathlib import Path


def _safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


def _escape(s):
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _fmt(x):
    if x is None:
        return "NA"
    try:
        xf = float(x)
    except Exception:
        return "NA"
    if abs(xf) >= 100:
        return f"{xf:.3f}"
    if abs(xf) >= 1:
        return f"{xf:.6f}".rstrip("0").rstrip(".")
    if abs(xf) == 0:
        return "0"
    return f"{xf:.6g}"


def _as_pairs(top):
    # Accept:
    # - dict: {"name": value}
    # - list of dicts: [{"name":..., "value":...}, ...]
    # - list of pairs: [("name", value), ...]
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


def write_svg(report_json_path: Path, out_svg_path: Path, top_k: int = 6, title: str = ""):
    with report_json_path.open("r", encoding="utf-8") as f:
        r = json.load(f)

    traces = r.get("traces", r.get("n_traces", None))
    d_total = r.get("D_total", r.get("d_total", None))
    s_score = r.get("S", r.get("s_score", None))
    deny_rate = r.get("deny_rate", None)
    abstain_rate = r.get("abstain_rate", None)

    # Support multiple possible keys (including the one your report uses)
    top = (
        r.get("top_drifts")  # <-- key used by your SSD reporter
        or r.get("top_drift_sources")
        or r.get("top_sources")
        or r.get("top_drift")
        or r.get("top_drift_metrics")
        or r.get("top")
    )

    pairs = _as_pairs(top)
    pairs = [(k, v) for (k, v) in pairs if isinstance(k, str)]
    pairs.sort(key=lambda kv: kv[1], reverse=True)
    pairs = pairs[: max(1, int(top_k))]

    # Layout
    W = 980
    H = 560
    pad = 28

    header_h = 170
    chart_top = header_h + 30
    chart_h = H - chart_top - pad
    chart_left = pad
    chart_right = W - pad
    chart_w = chart_right - chart_left

    # Bar chart
    n = len(pairs)
    bar_gap = 10
    bar_h = max(22, min(42, int((chart_h - (n - 1) * bar_gap) / max(1, n))))
    total_bars_h = n * bar_h + (n - 1) * bar_gap
    y0 = chart_top + max(0, int((chart_h - total_bars_h) / 2))

    maxv = max([v for _, v in pairs] + [1e-12])
    maxv = max(maxv, 1e-12)

    t = title.strip() or "SSD Evidence Snapshot (Case 1 Corridor)"
    subtitle = "Single-file, stdlib-only SVG generated from ssd_report.json"

    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
    lines.append('<rect x="0" y="0" width="100%" height="100%" fill="white"/>')

    # Title
    lines.append(
        f'<text x="{pad}" y="40" font-family="Arial, sans-serif" font-size="24" font-weight="700" fill="#111">{_escape(t)}</text>'
    )
    lines.append(
        f'<text x="{pad}" y="68" font-family="Arial, sans-serif" font-size="13" fill="#444">{_escape(subtitle)}</text>'
    )

    # Metric cards
    cards = [
        ("traces", _fmt(traces)),
        ("D_total", _fmt(d_total)),
        ("S", _fmt(s_score)),
        ("deny_rate", _fmt(deny_rate)),
        ("abstain_rate", _fmt(abstain_rate)),
    ]
    cx = pad
    cy = 84
    card_w = 170
    card_h = 44
    for k, v in cards:
        lines.append(f'<rect x="{cx}" y="{cy}" width="{card_w}" height="{card_h}" rx="8" ry="8" fill="#f6f6f6" stroke="#e6e6e6"/>')
        lines.append(f'<text x="{cx+12}" y="{cy+18}" font-family="Arial, sans-serif" font-size="12" fill="#666">{_escape(k)}</text>')
        lines.append(f'<text x="{cx+12}" y="{cy+36}" font-family="Arial, sans-serif" font-size="16" font-weight="700" fill="#111">{_escape(v)}</text>')
        cx += card_w + 10

    # Chart header
    lines.append(
        f'<text x="{pad}" y="{chart_top-10}" font-family="Arial, sans-serif" font-size="14" font-weight="700" fill="#111">Top drift sources (higher = more drift)</text>'
    )

    # Bars
    label_w = 360
    bar_x0 = chart_left + label_w
    bar_max_w = chart_w - label_w - 60

    for i, (name, val) in enumerate(pairs):
        y = y0 + i * (bar_h + bar_gap)

        # label
        lines.append(
            f'<text x="{chart_left}" y="{y + int(bar_h*0.7)}" font-family="Arial, sans-serif" font-size="12" fill="#111">{_escape(name)}</text>'
        )

        # background
        lines.append(
            f'<rect x="{bar_x0}" y="{y}" width="{bar_max_w}" height="{bar_h}" rx="6" ry="6" fill="#fafafa" stroke="#efefef"/>'
        )

        # fill
        w = int(math.ceil((val / maxv) * bar_max_w)) if val > 0 else 0
        if w > 0:
            w = max(2, w)
            lines.append(
                f'<rect x="{bar_x0}" y="{y}" width="{w}" height="{bar_h}" rx="6" ry="6" fill="#222"/>'
            )

        # value
        lines.append(
            f'<text x="{bar_x0 + bar_max_w + 10}" y="{y + int(bar_h*0.7)}" font-family="Arial, sans-serif" font-size="12" fill="#111">{_escape(_fmt(val))}</text>'
        )

    # Footer
    foot = "Note: SSD is trace-based diagnosis. This figure is illustrative evidence only; it does not modify computation."
    lines.append(f'<text x="{pad}" y="{H-14}" font-family="Arial, sans-serif" font-size="11" fill="#666">{_escape(foot)}</text>')

    lines.append("</svg>")

    out_svg_path.parent.mkdir(parents=True, exist_ok=True)
    out_svg_path.write_text("\n".join(lines), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", required=True, help="Path to ssd_report.json")
    ap.add_argument("--out_svg", required=True, help="Output SVG path")
    ap.add_argument("--top_k", type=int, default=6)
    ap.add_argument("--title", default="")
    args = ap.parse_args()

    write_svg(
        report_json_path=Path(args.report),
        out_svg_path=Path(args.out_svg),
        top_k=int(args.top_k),
        title=args.title,
    )

    print("SSD evidence SVG written:")
    print(str(Path(args.out_svg)))


if __name__ == "__main__":
    main()
