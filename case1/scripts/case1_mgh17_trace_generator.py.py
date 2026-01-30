#!/usr/bin/env python3
import argparse
import csv
import math
import os
import sys

EPS = 1e-12

STARTS = {
    1: [50.0, 150.0, -100.0, 1.0, 2.0],
    2: [0.5, 1.5, -1.0, 0.01, 0.02],
    3: [0.37541005211, 1.9358469127, -1.4646871366, 0.01286753464, 0.022122699662],
}

def safe_exp(z: float) -> float:
    if z > 700:
        return math.exp(700)
    if z < -700:
        return math.exp(-700)
    return math.exp(z)

def read_mgh17_csv(path: str):
    data = []
    with open(path, "r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        if "x" not in r.fieldnames or "y" not in r.fieldnames:
            raise ValueError("Input CSV must contain headers: x,y")
        for row in r:
            x = float(row["x"])
            y = float(row["y"])
            data.append((x, y))
    if len(data) < 10:
        raise ValueError("Parsed too few data points.")
    return data

def model_and_jac(x: float, b):
    b1, b2, b3, b4, b5 = b
    e4 = safe_exp(-b4 * x)
    e5 = safe_exp(-b5 * x)
    yhat = b1 + b2 * e4 + b3 * e5
    j = [
        1.0,
        e4,
        e5,
        b2 * (-x) * e4,
        b3 * (-x) * e5,
    ]
    return yhat, j

def mat_solve_5x5(A, b):
    n = 5
    M = [A[i][:] + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = col
        for r in range(col + 1, n):
            if abs(M[r][col]) > abs(M[pivot][col]):
                pivot = r
        if abs(M[pivot][col]) < 1e-18:
            return None
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
        div = M[col][col]
        for c in range(col, n + 1):
            M[col][c] /= div
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col]
            for c in range(col, n + 1):
                M[r][c] -= factor * M[col][c]
    return [M[i][n] for i in range(n)]

def cond_proxy(JTJ):
    diags = [abs(JTJ[i][i]) for i in range(5)]
    mx = max(diags)
    mn = min(d for d in diags if d > 1e-30) if any(d > 1e-30 for d in diags) else 1e-30
    return max(1.0, mx / mn)

def compute_sse_JTJ_JTr(data, bvec):
    SSE = 0.0
    JTJ = [[0.0] * 5 for _ in range(5)]
    JTr = [0.0] * 5
    for (x, y) in data:
        yhat, j = model_and_jac(x, bvec)
        r = y - yhat
        SSE += r * r
        for i in range(5):
            JTr[i] += j[i] * r
            for k in range(5):
                JTJ[i][k] += j[i] * j[k]
    return SSE, JTJ, JTr

def sse_permission(improve_ratio: float, step_norm_n: float, cond: float):
    imp = max(-1.0, min(1.0, improve_ratio))
    a_imp = 0.5 * (imp + 1.0)
    a_step = 1.0 / (1.0 + step_norm_n)
    a_cond = 1.0 / (1.0 + math.log10(max(cond, 1.0)))
    a = (0.50 * a_step + 0.50 * a_cond) * (0.25 + 0.75 * a_imp)
    if a < 0.0:
        a = 0.0
    if a > 1.0:
        a = 1.0
    return a

def sse_resistance_update(s_old: float, improve_ratio: float, step_norm_n: float, cond: float):
    logc = math.log10(max(cond, 1.0))
    pen_cond = max(0.0, logc - 3.0)

    pen_nonimp = 0.0
    if improve_ratio < 0.0:
        pen_nonimp = min(1.0, -improve_ratio)

    pen_step = step_norm_n
    delta = 0.45 * pen_step + 0.25 * pen_cond + 0.30 * pen_nonimp

    decay = 0.0
    if step_norm_n < 1e-4 and improve_ratio >= -1e-6:
        decay = 0.25

    return max(0.0, s_old + max(0.0, delta) - decay)

def gauss_newton(data, b0, max_iter, damping, sse_on,
                a_min, s_max, step_norm_max, cond_max, neg_imp_tol,
                warmup_allow, conv_step_tol, conv_imp_tol):
    b = b0[:]
    s = 0.0
    trace = []

    for it in range(max_iter):
        SSE_old, JTJ, JTr = compute_sse_JTJ_JTr(data, b)
        if math.isnan(SSE_old) or math.isinf(SSE_old):
            trace.append({
                "iter": it, "status": "NUMERIC_FAIL", "SSE": SSE_old,
                "SSE_next": float("nan"), "improve_ratio": float("nan"),
                "a": 0.0, "s": s, "step_norm": float("inf"), "cond": float("inf"),
                "b1": b[0], "b2": b[1], "b3": b[2], "b4": b[3], "b5": b[4]
            })
            break

        if damping > 0.0:
            for i in range(5):
                JTJ[i][i] += damping

        cond = cond_proxy(JTJ)
        step = mat_solve_5x5(JTJ, JTr)

        if step is None:
            status = "SINGULAR_JTJ" if not sse_on else "ABSTAIN_SINGULAR"
            trace.append({
                "iter": it, "status": status, "SSE": SSE_old,
                "SSE_next": float("nan"), "improve_ratio": float("nan"),
                "a": 0.0, "s": s, "step_norm": float("inf"), "cond": cond,
                "b1": b[0], "b2": b[1], "b3": b[2], "b4": b[3], "b5": b[4]
            })
            break

        step_norm = math.sqrt(sum(v * v for v in step))
        denom = max(1.0, math.sqrt(sum(v * v for v in b)))
        step_norm_n = step_norm / denom

        b_new = [b[i] + step[i] for i in range(5)]
        SSE_new, _, _ = compute_sse_JTJ_JTr(data, b_new)
        improve_ratio = (SSE_old - SSE_new) / max(SSE_old, EPS)

        if not sse_on:
            trace.append({
                "iter": it, "status": "CLASSICAL_STEP", "SSE": SSE_old,
                "SSE_next": SSE_new, "improve_ratio": improve_ratio,
                "a": 1.0, "s": 0.0, "step_norm": step_norm_n, "cond": cond,
                "b1": b[0], "b2": b[1], "b3": b[2], "b4": b[3], "b5": b[4]
            })
            b = b_new
            continue

        if step_norm_n < conv_step_tol and abs(improve_ratio) < conv_imp_tol:
            trace.append({
                "iter": it, "status": "CONVERGED_ALLOW", "SSE": SSE_old,
                "SSE_next": SSE_new, "improve_ratio": improve_ratio,
                "a": 1.0, "s": s, "step_norm": step_norm_n, "cond": cond,
                "b1": b[0], "b2": b[1], "b3": b[2], "b4": b[3], "b5": b[4]
            })
            break

        a = sse_permission(improve_ratio, step_norm_n, cond)
        s = sse_resistance_update(s, improve_ratio, step_norm_n, cond)

        deny = False
        if it < warmup_allow:
            if step_norm_n > step_norm_max or cond > cond_max or improve_ratio < neg_imp_tol:
                deny = True
        else:
            if a < a_min or s > s_max or step_norm_n > step_norm_max or cond > cond_max or improve_ratio < neg_imp_tol:
                deny = True

        status = "ALLOW" if not deny else "DENY"
        trace.append({
            "iter": it, "status": status, "SSE": SSE_old,
            "SSE_next": SSE_new, "improve_ratio": improve_ratio,
            "a": a, "s": s, "step_norm": step_norm_n, "cond": cond,
            "b1": b[0], "b2": b[1], "b3": b[2], "b4": b[3], "b5": b[4]
        })

        if deny:
            break
        b = b_new

    return trace

def write_csv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_csv", required=True, help="Path to MGH17 CSV with headers x,y")
    ap.add_argument("--out_dir", default="out_case1_v3")
    ap.add_argument("--start", type=int, default=1, choices=[1, 2, 3])
    ap.add_argument("--max_iter", type=int, default=50)
    ap.add_argument("--damping", type=float, default=0.0)

    ap.add_argument("--a_min", type=float, default=0.08)
    ap.add_argument("--s_max", type=float, default=10.0)
    ap.add_argument("--step_norm_max", type=float, default=8.0)
    ap.add_argument("--cond_max", type=float, default=1e14)
    ap.add_argument("--neg_imp_tol", type=float, default=-0.005)
    ap.add_argument("--warmup_allow", type=int, default=2)

    ap.add_argument("--conv_step_tol", type=float, default=1e-6)
    ap.add_argument("--conv_imp_tol", type=float, default=1e-6)

    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    try:
        data = read_mgh17_csv(args.in_csv)
    except Exception as e:
        print("ERROR: failed to read input CSV:", e)
        sys.exit(2)

    b0 = STARTS[args.start]

    tr_classical = gauss_newton(
        data=data, b0=b0, max_iter=args.max_iter, damping=args.damping, sse_on=False,
        a_min=args.a_min, s_max=args.s_max, step_norm_max=args.step_norm_max,
        cond_max=args.cond_max, neg_imp_tol=args.neg_imp_tol, warmup_allow=args.warmup_allow,
        conv_step_tol=args.conv_step_tol, conv_imp_tol=args.conv_imp_tol
    )
    tr_sse = gauss_newton(
        data=data, b0=b0, max_iter=args.max_iter, damping=args.damping, sse_on=True,
        a_min=args.a_min, s_max=args.s_max, step_norm_max=args.step_norm_max,
        cond_max=args.cond_max, neg_imp_tol=args.neg_imp_tol, warmup_allow=args.warmup_allow,
        conv_step_tol=args.conv_step_tol, conv_imp_tol=args.conv_imp_tol
    )

    fields = ["iter", "status", "SSE", "SSE_next", "improve_ratio", "a", "s", "step_norm", "cond",
              "b1", "b2", "b3", "b4", "b5"]
    write_csv(os.path.join(args.out_dir, "trace_classical.csv"), tr_classical, fields)
    write_csv(os.path.join(args.out_dir, "trace_sse.csv"), tr_sse, fields)

    def last_status(tr):
        return tr[-1]["status"] if tr else "NO_TRACE"

    print("SSE Proof Series — Case 1 (MGH17) v3 complete.")
    print("Dataset points:", len(data))
    print("Start:", args.start, "Initial b:", b0)
    print("Classical last status:", last_status(tr_classical), "iters:", len(tr_classical))
    print("SSE last status:", last_status(tr_sse), "iters:", len(tr_sse))
    print("Outputs written to:", args.out_dir)

if __name__ == "__main__":
    main()
