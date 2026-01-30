# ⚡ **Shunyaya Structural Diagnosis (SSD)**

## **Quickstart**

Deterministic • Trace-Based • Observational • Reproducible

---

## **WHAT YOU NEED**

SSD is intentionally minimal.

**Requirements**
- Python 3.9+
- Standard library only

Everything is:
- deterministic
- offline
- reproducible
- identical across machines

No randomness.  
No training.  
No probabilistic heuristics.

---

## **MINIMAL PROJECT LAYOUT**

A minimal SSD proof setup contains:

- a classical system that produces outputs unchanged
- a structural trace stream recorded during execution
- SSD diagnostic script(s) that run post-hoc

SSD never runs inside the solver.  
It operates only **after execution**, on recorded traces.

---

## **ONE-MINUTE MENTAL MODEL**

Classical mathematics asks:  
**“What is the result?”**

SSM / SSUM ask:  
**“How is the structure behaving?”**

SSD asks:  
**“Where is stability eroding, and why?”**

SSD does not allow.  
SSD does not deny.  
SSD diagnoses.

Silence is a valid outcome.  
Low drift and stable structure indicate admissible reliance.

---

## **CORE STRUCTURAL IDEA (IN ONE LINE)**

A system may compute correctly  
**while becoming structurally unsafe to rely upon.**

---

## **STRUCTURAL SIGNALS USED BY SSD**

SSD analyzes only observable trace signals, such as:

- posture consistency
- accumulation growth
- iteration variance
- conditioning drift
- regime transitions

Drift is measured using **variance**, not magnitude.

Example diagnostic primitive:

`D = Var(x_1 ... x_n)`

---

## **PRIMARY OUTPUTS (WHAT SSD REPORTS)**

SSD produces a deterministic diagnostic report containing:

- total drift measure `D_total`
- stability score `S = 1 / (1 + D_total)`
- `deny_rate` (fraction of traces diagnosed as DENY)
- `abstain_rate` (fraction of traces diagnosed as ABSTAIN)
- top drift contributors (ranked, explicit)
- per-trace run summaries (for multi-trace cases)

**Important clarification**

DENY and ABSTAIN are derived diagnostic verdicts, computed post-hoc from trace structure.  
They do not need to exist as stored trace state values and never influence computation.

---

## **QUICK RUN — CASE 1 (NONLINEAR SOLVER)**

From a folder that contains one or more trace files named `trace_sse.csv`:

`python scripts/ssd_from_traces.py \
  --root case1 \
  --trace_name trace_sse.csv \
  --out_dir case1/ssd_out_case1_corridor`

**Expected behavior**

**Mixed regime**
- high drift
- low `S`
- non-zero `deny_rate` or `abstain_rate`

**Stable corridor**
- low drift
- `S` close to 1
- `deny_rate = 0`
- `abstain_rate = 0`

Classical results remain unchanged in all cases.

---

## **QUICK RUN — CASE 2 (CALCULUS CORRIDORS)**

Case 2 demonstrates SSD on calculus linearization traces under corridor regimes.

### Generate traces (sqrt)

`python scripts/case2_calculus_trace_generator.py \
  --fn sqrt \
  --out_root case2/case2_traces \
  --a_min 0.70 \
  --s_max 0.80 \
  --r_safe 0.15 \
  --h 1e-3`

### Run SSD (sqrt)

`python scripts/ssd_from_traces.py \
  --root case2/case2_traces/sqrt \
  --trace_name trace_sse.csv \
  --out_dir case2/case2_results/ssd_out_case2_sqrt`

---

### Generate traces (1 / (1 − x))

`python scripts/case2_calculus_trace_generator.py \
  --fn recip \
  --out_root case2/case2_traces \
  --a_min 0.70 \
  --s_max 0.80 \
  --r_safe 0.15 \
  --h 1e-3`

### Run SSD (1 / (1 − x))

`python scripts/ssd_from_traces.py \
  --root case2/case2_traces/recip \
  --trace_name trace_sse.csv \
  --out_dir case2/case2_results/ssd_out_case2_recip`

**Expected behavior (Case 2)**

- non-zero `deny_rate` in boundary instability
- non-zero `abstain_rate` in undefined corridors

Common drift contributors (case-dependent):
- `D_final_s`
- `D_max_s`
- `D_final_err_abs`

---

## **QUICK RUN — CASE 3 (LINEAR SYSTEM CONDITIONING)**

Case 3 demonstrates SSD on linear systems where instability arises from conditioning, not numerical failure.

`python scripts/ssd_from_traces.py \
  --root case3 \
  --trace_name trace_sse.csv \
  --out_dir case3/ssd_out_case3`

**Expected behavior (Case 3)**

**Stable corridor**
- low drift
- `S` close to 1
- `deny_rate = 0`
- `abstain_rate = 0`

**Ill-conditioned corridor**
- elevated drift
- non-zero `deny_rate`
- structural pressure accumulates before numerical failure

**Singular corridor**
- `abstain_rate > 0`
- posture undefined
- no intervention in classical solve

Classical linear algebra results remain unchanged.

---

## **OPTIONAL — CANONICAL EVIDENCE & VISUALIZATION**

### **Canonical Evidence (SVG)**

- generated deterministically from `ssd_report.json`
- stored under `ssd_out_*`
- trace-backed and citation-ready
- treated as authoritative evidence

### **Optional Visualization (Matplotlib PNG)**

- rendered from existing SSD outputs only
- stored under `figures/`
- inspection and presentation use only
- never treated as evidence

SVG remains the canonical artifact.

---

## **WHAT SSD IS — AND IS NOT**

SSD is:
- a diagnostic lens
- deterministic
- conservative
- explainable
- collapse-safe under `phi((m,a,s)) = m`

SSD is not:
- a solver
- an optimizer
- a predictor
- a governance mechanism
- a decision engine

---

## **DETERMINISM GUARANTEE**

Given identical traces:
- identical diagnostics
- identical stability scores
- identical drift attribution

No randomness.  
No hidden state.

---

## **QUICKSTART SUMMARY**

SSD provides structural clarity **before failure**,  
without interfering with computation.

