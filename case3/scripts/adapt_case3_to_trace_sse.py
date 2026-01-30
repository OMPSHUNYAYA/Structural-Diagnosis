import csv
from pathlib import Path

def read_rows(path: Path):
    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        return list(r)

def to_float(v):
    try:
        return float(v)
    except Exception:
        return None

def write_trace_sse(out_path: Path, rows_in, status: str):
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "iter",
        "status",
        "a",
        "s",
        "cond",
        "step_norm",
        "err_abs",
        "r",
        "risk",
    ]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r0 in rows_in:
            step = int(float(r0.get("step", 0)))
            a = to_float(r0.get("a"))
            s = to_float(r0.get("s"))
            cond = to_float(r0.get("cond_hat"))
            step_norm = to_float(r0.get("res"))
            err_abs = to_float(r0.get("m"))
            rr = None
            if cond is not None and step_norm is not None:
                rr = cond * step_norm
            out = {
                "iter": step,
                "status": status,
                "a": a,
                "s": s,
                "cond": cond,
                "step_norm": step_norm,
                "err_abs": err_abs,
                "r": rr,
                "risk": rr,
            }
            w.writerow(out)

def main():
    root = Path(".").resolve()
    out_root = root / "case3_runs"

    mapping = [
        ("case3_allow_trace.csv", "ALLOW", out_root / "allow" / "trace_sse.csv"),
        ("case3_deny_trace.csv", "DENY", out_root / "deny" / "trace_sse.csv"),
        ("case3_abstain_trace.csv", "ABSTAIN", out_root / "abstain" / "trace_sse.csv"),
    ]

    for in_name, status, out_path in mapping:
        rows = read_rows(root / in_name)
        write_trace_sse(out_path, rows, status)

    print("Wrote:")
    for _, _, out_path in mapping:
        print(" -", out_path.as_posix())

if __name__ == "__main__":
    main()
