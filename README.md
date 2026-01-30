# ⭐ Shunyaya Structural Diagnosis (SSD)

**Make Stability Erosion Visible — Structure First — Without Changing Any Computation**

![STARS](https://img.shields.io/badge/SSD-STARS-green)
![Deterministic](https://img.shields.io/badge/Deterministic-Yes-green)
![Post--Hoc](https://img.shields.io/badge/Post--Hoc-Only-green)
![Collapse--Safe](https://img.shields.io/badge/Collapse--Safe-Yes-green)
![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-green)

Deterministic • Structural Diagnosis • Drift Visibility • Stability Corridors • Explainable Reports • Observation-Only

---

## 🔎 What Is Shunyaya Structural Diagnosis (SSD)?

Shunyaya Structural Diagnosis (SSD) is a **deterministic, trace-based diagnostic framework** that explains **where stability is eroding and why**, across mathematics, software, systems, and processes — **without modifying any computation**.

Classical systems typically ask:

- What is the output?
- Is it fast?
- Did it pass a threshold?

SSD asks a **prior and more responsible question**:

**“Is this result, system, or process structurally admissible to be relied upon here — even if it is correct?”**

SSD does **not** replace monitoring.  
SSD does **not** modify computations.  
SSD does **not** optimize systems.  
SSD does **not** predict outcomes.

SSD changes the **question being asked**, not the mathematics being computed.

SSD introduces **responsibility-aware diagnostics** without altering correctness.

---

## 🔗 Quick Links

### **Docs**
- [Quickstart Guide](docs/Quickstart.md)
- [FAQ](docs/FAQ.md)
- [Full Specification (PDF)](docs/SSD_v1.6.pdf)
- [Formal Proof & Evidence (PDF)](docs/PROOF-SSD_v1.6.pdf)

---

### **Core Diagnostic Engine**
- Case 1: [`case1/scripts/ssd_from_traces.py`](case1/scripts/ssd_from_traces.py)
- Case 2: [`case2/scripts/ssd_from_traces.py`](case2/scripts/ssd_from_traces.py)
- Case 3: [`case3/scripts/ssd_from_traces.py`](case3/scripts/ssd_from_traces.py)
- Case 4: [`case4/scripts/ssd_from_traces.py`](case4/scripts/ssd_from_traces.py)

Each script is identical in logic and runs deterministically on case-specific traces.

---

### **Proof Cases (Executable & Reproducible)**

#### **Case 1 — Nonlinear Solver (MGH17)**
- [`case1/`](case1/)
- Canonical outputs: [`case1/ssd_out_case1_corridor/`](case1/ssd_out_case1_corridor/)
- Scripts: [`case1/scripts/`](case1/scripts/)
- Figures (non-evidence): [`case1/figures/`](case1/figures/)
- Optional raw traces: [`case1/evidence_optional/`](case1/evidence_optional/)

#### **Case 2 — Calculus Corridor Diagnostics**
- [`case2/`](case2/)
- sqrt corridor outputs: [`case2/case2_results/ssd_out_case2_sqrt/`](case2/case2_results/ssd_out_case2_sqrt/)
- reciprocal corridor outputs: [`case2/case2_results/ssd_out_case2_recip/`](case2/case2_results/ssd_out_case2_recip/)
- Scripts: [`case2/scripts/`](case2/scripts/)
- Figures (non-evidence): [`case2/figures/`](case2/figures/)
- Optional raw traces: [`case2/evidence_optional/`](case2/evidence_optional/)

#### **Case 3 — Linear System Conditioning**
- [`case3/`](case3/)
- Canonical outputs: [`case3/ssd_out_case3/`](case3/ssd_out_case3/)
- Scripts: [`case3/scripts/`](case3/scripts/)
- Figures (non-evidence): [`case3/figures/`](case3/figures/)
- Optional raw traces: [`case3/evidence_optional/`](case3/evidence_optional/)

#### **Case 4 — ODE Time-Evolution Erosion**
- [`case4/`](case4/)
- Canonical outputs: [`case4/ssd_out_case4/`](case4/ssd_out_case4/)
- Scripts: [`case4/scripts/`](case4/scripts/)
- Figures (non-evidence): [`case4/figures/`](case4/figures/)
- Optional raw traces: [`case4/evidence_optional/`](case4/evidence_optional/)

---

### **Canonical Evidence (Authoritative)**
- SVG evidence snapshots located under each `ssd_out_*` directory  
  (generated deterministically from `ssd_report.json` and treated as citation-ready)

---

## 🔒 SSD Guarantees (Non-Negotiable)

SSD operates under strict, conservative guarantees:

- **Deterministic**: identical traces always produce identical diagnostics
- **Post-hoc only**: SSD runs strictly after execution on recorded traces
- **Non-invasive**: no solver, system, or process behavior is ever modified
- **Collapse-safe**: `phi((m, a, s)) = m` holds everywhere
- No learning, no training, no adaptive tuning
- No probability, no stochastic methods
- Canonical evidence is **SVG derived from `ssd_report.json`**
- Optional plots are **explicitly non-evidentiary**

SSD never alters outcomes.  
SSD explains **when outcomes are unsafe to rely upon**.

---

## 🎯 Problem Statement — Why Classical Monitoring Misses Stability

Classical monitoring and metrics are often snapshot-driven.

In real systems:

- outputs can be correct yet unreliable
- incidents emerge from **drift**, not a single bad value
- instability accumulates silently before denial becomes visible
- “sometimes it works, sometimes it doesn’t” remains unexplained

SSD introduces a missing capability:

**Diagnose drift and stability erosion before denial becomes obvious — without changing system behavior.**

---

## 🔎 Structural Diagnosis vs Classical Monitoring

| Aspect | Classical Monitoring | Structural Diagnosis (SSD) |
|------|----------------------|----------------------------|
| Focus | Snapshot values | Evolution and drift |
| Failure detection | After failure | Before denial |
| Dependency awareness | Shallow | Explicit structural graph |
| Interpretability | Metric-centric | Cause-centric |
| Safety posture | Reactive | Preventive |
| Collapse behavior | Implicit | Guaranteed |

SSD explains **why instability forms**, not just that it occurred.

---

## 🧱 Structural State and Collapse Rule

SSD operates on **collapse-safe structural envelopes**.

Collapse invariant:

`phi((m, a, s)) = m`

where:

- `m` = classical output (value, metric, result)
- `a` = bounded alignment (instantaneous posture)
- `s` = accumulated structural pressure (memory)

This guarantees:

- classical meaning is never overwritten
- SSD is observational only
- all diagnostics collapse cleanly to classical outputs

---

## 🔍 What SSD Diagnoses

SSD diagnoses structure from **post-hoc traces**, including:

- posture consistency (`a`)
- accumulation growth (`s`)
- drift across repetition (variance)
- regime mixing (stable vs unstable corridors)
- observed `deny_rate` and `abstain_rate` (diagnostic, not enforced)

**Important clarification**

DENY and ABSTAIN are **derived diagnostic verdicts**, computed post-hoc from trace structure.  
They do not need to exist as stored trace state values, and they never influence computation.

Drift is measured through **variance**, not magnitude.

Example diagnostic primitive:

`D = Var(x_1 ... x_n)`

SSD evaluates variance **before failure**, not averages after convergence.

---

## 📊 Stability Score (Optional, Auditable)

SSD supports an explainable stability score:

`S = 1 / (1 + D_total)`

where `D_total` is an explicit aggregation of drift contributors.

- No learning
- No normalization tricks
- No hidden weighting

The score is a **summary**, not a substitute for drift attribution.

---

## 🧭 Structural States (Human-Readable)

SSD classifies systems into clear, auditable states:

- CALM
- BALANCED
- PRESSURIZED
- FRAGILE
- DENIED

These states are derived deterministically from trace structure.

---

## 📌 Interpreting Drift Signals (Canonical Reference)

| Drift Signal | Typical Interpretation (Conservative) |
|-------------|---------------------------------------|
| `D_*_s` | Accumulation fatigue / memory variance |
| `D_*_step_norm` | Update or integration instability |
| `D_*_cond` | Conditioning sensitivity |
| `D_*_err_abs` | Approximation or model error drift |
| `D_*_r` or `D_*_risk` | Instantaneous posture pressure |
| `D_iters` | Iterative regime inconsistency |

Drift signals are **diagnostic indicators**, not causal claims.

---

## 🧪 Proof Series — What SSD Demonstrates

SSD is validated through **executable, reproducible proof cases**.  
All diagnosis occurs **strictly after execution**.

### Case 1 — Nonlinear Solver Regime Diagnosis (Completed)

SSD demonstrates the ability to:

- distinguish mixed structural regimes from stable corridors
- quantify drift and stability using trace variance
- remain silent (high stability) when structure is consistent
- attribute instability to concrete drift sources

Silence in pure corridors is a **positive diagnostic outcome**, not missing signal.

---

### Case 2 — Calculus Corridor Diagnosis (Completed)

SSD demonstrates that unsafe reliance can be diagnosed in calculus even when classical computation continues to produce valid results.

Using deterministic linearization traces, SSD shows that:

- safe corridors exhibit low drift and high stability
- boundary regimes produce denial with concentrated drift
- undefined regimes produce abstention without intervention
- different functions yield distinct structural signatures

No calculus result is modified.

---

### Case 3 — Linear System Conditioning Corridor Diagnosis (Completed)

SSD demonstrates diagnosis of unsafe reliance caused by matrix conditioning, even when solvers compute valid numerical solutions.

SSD shows that:

- stable systems remain silent under admissible conditioning
- ill-conditioned systems accumulate structural pressure before failure
- singular or near-singular systems produce abstention without intervention

No linear algebra computation is modified.

---

### Case 4 — ODE Time-Evolution Erosion Diagnosis (Completed)

SSD demonstrates diagnosis of time-accumulated structural erosion in dynamical systems.

SSD shows that:

- systems may remain numerically computable while becoming unsafe to rely upon
- structural fatigue accumulates before numerical breakdown
- denial can occur during continued computation
- abstention occurs immediately under divergent evolution

Time integration is never altered.

---

## 📁 Repository Structure (Reference)

The SSD repository is organized by proof case.  
Each case is **self-contained and reproducible**.

```
/
├── docs/                    # SSD core documents
├── case1/                   # Nonlinear solver (MGH17)
├── case2/                   # Calculus corridor diagnostics
├── case3/                   # Linear system conditioning
├── case4/                   # ODE time-evolution erosion
│
└── Each case contains:
    ├── scripts/             # Trace generation & diagnostics
    ├── ssd_out_* /          # Canonical SSD outputs (authoritative)
    ├── figures/             # Optional visualizations (non-evidence)
    └── evidence_optional/   # Raw traces and expanded runs
```

---

## 🧾 Outputs — What You Get

SSD produces deterministic diagnostic artifacts, including:

- number of traces analyzed
- total drift measure `D_total`
- stability score `S`
- observed `deny_rate` and `abstain_rate`
- top drift sources (explicit attribution)
- per-run, per-corridor, or per-subcase summaries

---

## 📄 Canonical Evidence: SVG (Authoritative)

SSD generates one or more canonical evidence snapshots (SVG) per case or subcase.

- derived deterministically from `ssd_report.json`
- stored alongside SSD outputs (`ssd_out_*`)
- citation-ready and audit-safe
- treated as authoritative evidence

---

## 🖼️ Optional Visualization: Matplotlib PNG

Optional Matplotlib scripts generate PNG reference plots for convenience.

- render existing SSD diagnostics only
- stored under `figures/`
- intended for inspection or presentation
- **never treated as evidence**

SVG remains the canonical artifact.

---

## 🧪 Determinism & Reproducibility

Given identical traces, SSD guarantees:

- identical diagnostics
- identical stability scores
- identical drift attribution

No randomness.  
No machine dependence.  
No hidden state.

---

## 🚫 What SSD Is Not

SSD is **not**:

- an optimizer
- a monitoring replacement
- a solver replacement
- a predictor
- a learning system
- a decision-making authority

SSD does not change outcomes.  
SSD explains **stability**.

---

## 🔹 Positioning Within the Shunyaya Framework

SSD is part of a layered family of conservative extensions that preserve exact equivalence to classical results while adding structural capability.

- **SSM** — bounded posture observability (`a`)
- **SSUM** — evolution and accumulation tracking (`s`)
- **SSD** — diagnosis: where stability erodes, and why
- **SSE** — governance: when reliance is admissible

All layers preserve collapse safety:

`phi((m, a, s)) = m`

Classical computation is never modified.  
Only structural insight (and optionally governance) is added.

---

## 📄 License & Attribution

**License**: CC BY 4.0

**Attribution required**:

Shunyaya Structural Diagnosis (SSD)  
Built within the Shunyaya ecosystem  

Provided “as is”, without warranty of any kind.

---

## 🔹 One-Line Summary

**Shunyaya Structural Diagnosis makes stability erosion visible — without changing a single classical result.**

---

## 🏷️ Topics

SSD, Structural-Diagnosis, Deterministic-Observability, Drift-Detection, Stability-Corridors, Explainable-Diagnostics, Collapse-Safe, Shunyaya
