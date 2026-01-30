import os
import csv
import math
import argparse

EPS = 1e-15


def _is_finite(x):
    return isinstance(x, (int, float)) and math.isfinite(x)


def _safe_mkdir(p):
    os.makedirs(p, exist_ok=True)


def _write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def f_sqrt(x):
    if x < 0:
        return float("nan")
    return math.sqrt(x)


def fp_sqrt(x):
    if x <= 0:
        return float("nan")
    return 1.0 / (2.0 * math.sqrt(x))


def fpp_sqrt(x):
    if x <= 0:
        return float("nan")
    return -1.0 / (4.0 * (x ** 1.5))


def f_recip(x):
    d = 1.0 - x
    if abs(d) < EPS:
        return float("nan")
    return 1.0 / d


def fp_recip(x):
    d = 1.0 - x
    if abs(d) < EPS:
        return float("nan")
    return 1.0 / (d * d)


def fpp_recip(x):
    d = 1.0 - x
    if abs(d) < EPS:
        return float("nan")
    return 2.0 / (d ** 3)


def choose_fn(name):
    name = (name or "").strip().lower()
    if name in ("sqrt", "root", "sqrtx"):
        return ("sqrt", f_sqrt, fp_sqrt, fpp_sqrt)
    if name in ("recip", "reciprocal", "1/(1-x)", "one_over_one_minus_x"):
        return ("recip", f_recip, fp_recip, fpp_recip)
    raise ValueError("Unsupported --fn. Use: sqrt or recip")


def sse_permission_and_risk(fp, fpp, x, h):
    G = abs(fp(x))
    C = abs(fpp(x))
    if not _is_finite(G) or not _is_finite(C):
        return (float("nan"), float("nan"), float("nan"), float("nan"))
    r = (C * abs(h)) / (1.0 + G)
    a = 1.0 / (1.0 + r)
    return (G, C, r, a)


def build_corridors(fn_tag):
    if fn_tag == "sqrt":
        xs_allow = [1.0 - i * 0.02 for i in range(0, 26)]
        xs_deny = [0.0016 - i * 0.0001 for i in range(0, 8)]
        xs_abstain = [0.0, -0.0001, -0.001]
        return xs_allow, xs_deny, xs_abstain

    if fn_tag == "recip":
        xs_allow = [0.0 + i * 0.02 for i in range(0, 26)]
        xs_deny = [0.85 + i * 0.007 for i in range(0, 20)]
        xs_abstain = [0.99, 0.995, 0.999, 1.0, 1.0001]
        return xs_allow, xs_deny, xs_abstain

    raise ValueError("Unsupported fn_tag")


def run_scenario(f, fp, fpp, xs, h, a_min, s_max, r_safe, out_dir):
    classical_rows = []
    sse_rows = []
    s = 0.0

    for k, x in enumerate(xs):
        y_true = f(x + h)
        y_lin = f(x) + fp(x) * h
        err = abs(y_true - y_lin) if (_is_finite(y_true) and _is_finite(y_lin)) else float("nan")

        status = "ALLOW"
        _, _, r, a = sse_permission_and_risk(fp, fpp, x, h)

        if (not _is_finite(y_true)) or (not _is_finite(y_lin)) or (not _is_finite(a)):
            status = "ABSTAIN"
            a = float("nan")
            r = float("nan")
        else:
            if r > r_safe:
                s = s + (r - r_safe)

            if (a < a_min) or (s > s_max):
                status = "DENY"

        classical_rows.append([k, x, h, y_true, y_lin, err])
        sse_rows.append([k, x, h, y_true, y_lin, err, a, s, status])

    _safe_mkdir(out_dir)
    _write_csv(
        os.path.join(out_dir, "trace_classical.csv"),
        ["k", "x", "h", "y_true", "y_lin", "err_abs"],
        classical_rows,
    )
    _write_csv(
        os.path.join(out_dir, "trace_sse.csv"),
        ["k", "x", "h", "y_true", "y_lin", "err_abs", "a", "s", "status"],
        sse_rows,
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fn", default="sqrt", help="sqrt or recip")
    ap.add_argument("--out_root", default="case2_traces", help="Output folder under current directory")
    ap.add_argument("--a_min", type=float, default=0.70)
    ap.add_argument("--s_max", type=float, default=0.80)
    ap.add_argument("--r_safe", type=float, default=0.15)
    ap.add_argument("--h", type=float, default=1e-3)
    args = ap.parse_args()

    fn_tag, f, fp, fpp = choose_fn(args.fn)
    out_root = os.path.abspath(args.out_root)

    xs_allow, xs_deny, xs_abstain = build_corridors(fn_tag)

    base = os.path.join(out_root, fn_tag)
    out_allow = os.path.join(base, "allow_safe_corridor")
    out_deny = os.path.join(base, "deny_boundary_corridor")
    out_abstain = os.path.join(base, "abstain_instability_corridor")

    run_scenario(f, fp, fpp, xs_allow, args.h, args.a_min, args.s_max, args.r_safe, out_allow)
    run_scenario(f, fp, fpp, xs_deny, args.h, args.a_min, args.s_max, args.r_safe, out_deny)
    run_scenario(f, fp, fpp, xs_abstain, args.h, args.a_min, args.s_max, args.r_safe, out_abstain)

    print("SSD Case 2 traces generated:")
    print(f" - {out_allow}")
    print(f" - {out_deny}")
    print(f" - {out_abstain}")
    print("Each contains: trace_classical.csv and trace_sse.csv")


if __name__ == "__main__":
    main()
