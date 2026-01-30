import argparse
import csv
import math
import os

EPS = 1e-15

def _safe_mkdir(p):
    os.makedirs(p, exist_ok=True)

def _write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)

def _is_finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)

def simulate_corridor(tag, k, dt, steps, y0, r_safe, s_relief, a_min, s_max, g_abstain):
    rows_raw = []
    rows_sse = []

    y = float(y0)
    s = 0.0

    for n in range(steps + 1):
        t = n * dt
        y_true = math.exp(-k * t)
        err_abs = abs(y - y_true) if (_is_finite(y) and _is_finite(y_true)) else float("nan")

        g = abs(1.0 - k * dt)
        r = (k * dt) * g
        a = 1.0 / (1.0 + r) if _is_finite(r) else 0.0

        status = "ALLOW"

        if (not _is_finite(y)) or (not _is_finite(y_true)) or (not _is_finite(err_abs)) or (not _is_finite(g)):
            status = "ABSTAIN"
        elif g > g_abstain:
            status = "ABSTAIN"
        else:
            if r <= r_safe:
                s = max(0.0, s - s_relief)
            else:
                s = s + (r - r_safe)

            if (a < a_min) or (s > s_max):
                status = "DENY"

        step_norm = abs(dt * (-k * y)) if _is_finite(y) else float("inf")
        cond_hat = max(1.0, 1.0 / max(EPS, abs(1.0 - k * dt))) if _is_finite(k) else float("inf")
        res = err_abs
        m = err_abs

        rows_raw.append([
            n, tag, t, k, dt, y, y_true, err_abs, g, r, a, s, status
        ])

        rows_sse.append([
            n, status, a, s, cond_hat, step_norm, err_abs, r, r
        ])

        if status in ("DENY", "ABSTAIN"):
            break

        y = y * (1.0 - k * dt)

    return rows_raw, rows_sse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out_case_dir", default="case4", help="Case folder name under current directory")
    ap.add_argument("--steps", type=int, default=160)
    ap.add_argument("--dt", type=float, default=0.05)
    ap.add_argument("--y0", type=float, default=1.0)

    ap.add_argument("--r_safe", type=float, default=0.40)
    ap.add_argument("--s_relief", type=float, default=0.08)
    ap.add_argument("--a_min", type=float, default=0.45)
    ap.add_argument("--s_max", type=float, default=2.00)
    ap.add_argument("--g_abstain", type=float, default=1.02)

    ap.add_argument("--k_allow", type=float, default=2.0)
    ap.add_argument("--k_deny", type=float, default=16.0)
    ap.add_argument("--k_abstain", type=float, default=60.0)

    args = ap.parse_args()

    root = os.path.abspath(args.out_case_dir)

    raw_dir = os.path.join(root, "traces", "raw")
    runs_dir = os.path.join(root, "case4_runs")

    _safe_mkdir(raw_dir)
    _safe_mkdir(runs_dir)

    corridors = [
        ("ALLOW", args.k_allow, os.path.join(raw_dir, "case4_allow_trace.csv"), os.path.join(runs_dir, "allow", "trace_sse.csv")),
        ("DENY", args.k_deny, os.path.join(raw_dir, "case4_deny_trace.csv"), os.path.join(runs_dir, "deny", "trace_sse.csv")),
        ("ABSTAIN", args.k_abstain, os.path.join(raw_dir, "case4_abstain_trace.csv"), os.path.join(runs_dir, "abstain", "trace_sse.csv")),
    ]

    raw_header = ["step", "corridor", "t", "k", "dt", "y_num", "y_true", "err_abs", "g_amp", "r", "a", "s", "status"]
    sse_header = ["iter", "status", "a", "s", "cond", "step_norm", "err_abs", "r", "risk"]

    wrote = []

    for tag, k, raw_path, sse_path in corridors:
        rows_raw, rows_sse = simulate_corridor(
            tag=tag,
            k=float(k),
            dt=float(args.dt),
            steps=int(args.steps),
            y0=float(args.y0),
            r_safe=float(args.r_safe),
            s_relief=float(args.s_relief),
            a_min=float(args.a_min),
            s_max=float(args.s_max),
            g_abstain=float(args.g_abstain),
        )

        _safe_mkdir(os.path.dirname(raw_path))
        _safe_mkdir(os.path.dirname(sse_path))

        _write_csv(raw_path, raw_header, rows_raw)
        _write_csv(sse_path, sse_header, rows_sse)

        wrote.append(raw_path)
        wrote.append(sse_path)

    print("CASE 4A (ODE) traces written:")
    for p in wrote:
        print(" -", p)

    print("")
    print("Corridor params:")
    print(" dt =", args.dt, "steps =", args.steps, "y0 =", args.y0)
    print(" k_allow =", args.k_allow, "k_deny =", args.k_deny, "k_abstain =", args.k_abstain)
    print(" a_min =", args.a_min, "s_max =", args.s_max, "r_safe =", args.r_safe, "g_abstain =", args.g_abstain)

if __name__ == "__main__":
    main()
