import json
import csv
from pathlib import Path
import matplotlib.pyplot as plt

def main():
    base = Path("case4/ssd_out_case4")

    report = json.load(open(base / "ssd_report.json", "r", encoding="utf-8"))

    top = report["top_drifts"]
    labels = [d["name"] for d in top]
    values = [d["value"] for d in top]

    S = report["S"]
    deny_rate = report["deny_rate"]
    abstain_rate = report["abstain_rate"]

    fig, ax = plt.subplots(figsize=(7, 4))

    ax.bar(labels, values)
    ax.set_ylabel("Normalized Drift Contribution")
    ax.set_title("SSD Evidence Snapshot — Case 4A (ODE Time Evolution)")

    ax.tick_params(axis="x", rotation=30)

    info = (
        f"Stability score S = {S:.4f}\n"
        f"deny_rate = {deny_rate:.3f}\n"
        f"abstain_rate = {abstain_rate:.3f}"
    )

    ax.text(
        0.98,
        0.95,
        info,
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.9),
    )

    out = base / "case4_evidence.svg"
    plt.tight_layout()
    plt.savefig(out, format="svg")
    plt.close(fig)

    print("Case 4A SSD evidence written:")
    print(" -", out.resolve())

if __name__ == "__main__":
    main()
