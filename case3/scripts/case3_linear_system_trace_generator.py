import csv
import math
from typing import List, Tuple, Optional

EPS_PIVOT = 1e-15

def mat_vec(A: List[List[float]], x: List[float]) -> List[float]:
    n = len(A)
    y = [0.0] * n
    for i in range(n):
        s = 0.0
        row = A[i]
        for j in range(n):
            s += row[j] * x[j]
        y[i] = s
    return y

def inf_norm_mat(A: List[List[float]]) -> float:
    n = len(A)
    mx = 0.0
    for i in range(n):
        s = 0.0
        for j in range(n):
            s += abs(A[i][j])
        if s > mx:
            mx = s
    return mx

def inf_norm_vec(v: List[float]) -> float:
    mx = 0.0
    for x in v:
        ax = abs(x)
        if ax > mx:
            mx = ax
    return mx

def gauss_solve(A: List[List[float]], b: List[float]) -> List[float]:
    n = len(A)
    M = [row[:] for row in A]
    y = b[:]

    for k in range(n):
        pivot_row = k
        pivot_val = abs(M[k][k])
        for i in range(k + 1, n):
            v = abs(M[i][k])
            if v > pivot_val:
                pivot_val = v
                pivot_row = i

        if pivot_val < EPS_PIVOT:
            raise ValueError("SINGULAR")

        if pivot_row != k:
            M[k], M[pivot_row] = M[pivot_row], M[k]
            y[k], y[pivot_row] = y[pivot_row], y[k]

        piv = M[k][k]
        inv_piv = 1.0 / piv
        for j in range(k, n):
            M[k][j] *= inv_piv
        y[k] *= inv_piv

        for i in range(k + 1, n):
            f = M[i][k]
            if f == 0.0:
                continue
            for j in range(k, n):
                M[i][j] -= f * M[k][j]
            y[i] -= f * y[k]

    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = y[i]
        for j in range(i + 1, n):
            s -= M[i][j] * x[j]
        x[i] = s
    return x

def inv_inf_norm_est(A: List[List[float]]) -> float:
    n = len(A)
    cols = []
    for k in range(n):
        e = [0.0] * n
        e[k] = 1.0
        y = gauss_solve(A, e)
        cols.append(y)

    mx = 0.0
    for i in range(n):
        s = 0.0
        for k in range(n):
            s += abs(cols[k][i])
        if s > mx:
            mx = s
    return mx

def hilbert(n: int) -> List[List[float]]:
    A = []
    for i in range(n):
        row = []
        for j in range(n):
            row.append(1.0 / (i + j + 1.0))
        A.append(row)
    return A

def diagdom_tridiag(n: int, alpha: float) -> List[List[float]]:
    A = [[0.0 for _ in range(n)] for __ in range(n)]
    for i in range(n):
        A[i][i] = 1.0 + 2.0 * alpha
        if i - 1 >= 0:
            A[i][i - 1] = -alpha
        if i + 1 < n:
            A[i][i + 1] = -alpha
    return A

def make_singular_by_duplicate_row(A: List[List[float]], src_row: int, dst_row: int) -> List[List[float]]:
    B = [row[:] for row in A]
    B[dst_row] = B[src_row][:]
    return B

def compute_row(A: List[List[float]], corridor: str, family: str, matrix_id: str, alpha: Optional[float],
                step: int, s_prev: float,
                r_safe: float = 1.0, s_relief: float = 0.25,
                a_min: float = 0.50, s_warn: float = 1.00, s_deny: float = 2.00) -> Tuple[dict, float]:
    n = len(A)
    x_true = [1.0] * n
    b = mat_vec(A, x_true)

    event = "NORMAL"
    m = float("nan")
    res = float("nan")
    cond_hat = float("inf")
    a = 0.0

    try:
        x = gauss_solve(A, b)
        Ax = mat_vec(A, x)
        rvec = [Ax[i] - b[i] for i in range(n)]
        res = inf_norm_vec(rvec)
        m = max(abs(x[i] - 1.0) for i in range(n))

        Ainf = inf_norm_mat(A)
        Ainv_inf = inv_inf_norm_est(A)
        cond_hat = Ainf * Ainv_inf

        r = cond_hat * res
        a = 1.0 / (1.0 + r)

    except ValueError:
        event = "SINGULAR"
        r = float("inf")
        a = 0.0

    if math.isfinite(r) and r <= r_safe:
        s_new = max(0.0, s_prev - s_relief)
    else:
        inc = (r - r_safe) if math.isfinite(r) else 1.0
        if inc < 0.0:
            inc = 0.0
        s_new = s_prev + inc

    if event == "SINGULAR":
        state = "FRAGILE"
    else:
        if a < a_min or s_new >= s_deny:
            state = "DENIED"
        elif s_new >= s_warn:
            state = "PRESSURIZED"
        elif a < 0.80:
            state = "BALANCED"
        else:
            state = "CALM"

    row = {
        "step": step,
        "corridor": corridor,
        "matrix_family": family,
        "matrix_size": n,
        "matrix_id": matrix_id,
        "alpha": "" if alpha is None else alpha,
        "m": m,
        "a": a,
        "s": s_new,
        "state": state,
        "cond_hat": cond_hat,
        "res": res,
        "event": event,
    }
    return row, s_new

def write_trace(path: str, rows: List[dict]) -> None:
    fieldnames = [
        "step", "corridor", "matrix_family", "matrix_size", "matrix_id", "alpha",
        "m", "a", "s", "state", "cond_hat", "res", "event"
    ]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)

def main() -> None:
    allow_rows = []
    deny_rows = []
    abstain_rows = []

    s = 0.0
    n = 6
    for step, alpha in enumerate([0.05, 0.10, 0.20]):
        A = diagdom_tridiag(n, alpha)
        row, s = compute_row(A, "ALLOW", "DIAGDOM", f"DIAGDOM_n{n}_a{alpha}", alpha, step, s)
        allow_rows.append(row)
    write_trace("case3_allow_trace.csv", allow_rows)

    s = 0.0
    for step, hn in enumerate([6, 8, 10]):
        A = hilbert(hn)
        row, s = compute_row(A, "DENY", "HILBERT", f"HILBERT_n{hn}", None, step, s)
        deny_rows.append(row)
    write_trace("case3_deny_trace.csv", deny_rows)

    s = 0.0
    for step in range(2):
        A0 = diagdom_tridiag(6, 0.10)
        A = make_singular_by_duplicate_row(A0, 1, 2)
        row, s = compute_row(A, "ABSTAIN", "SINGULAR", f"SINGULAR_n6_dupRow", None, step, s)
        abstain_rows.append(row)
    write_trace("case3_abstain_trace.csv", abstain_rows)

if __name__ == "__main__":
    main()
