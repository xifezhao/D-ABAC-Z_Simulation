

# D-ABAC-Z Simulation Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Formal Verification](https://img.shields.io/badge/Formal%20Methods-Z%20%2B%20Alloy-purple)](./formal_methods/)

This repository contains the official reference implementation and simulation scripts for the paper:

> **Formalizing Dynamic Trust: A Z-Based Specification and Alloy Verification of Context-Aware ABAC**
>
> *Submitted to ESORICS 2026*

## 📖 Overview

**D-ABAC-Z** is a novel access control framework designed for Zero Trust Architectures (ZTA). It bridges the gap between probabilistic trust models and deterministic formal verification.

This simulation project serves three main purposes:
1.  **Algorithmic Verification:** Implements the mathematically rigorous **HMM-based Trust Model** (Section 3) and **Linear Risk-Adaptive Policy** (LRAP).
2.  **Scenario Reproduction:** Reproduces the **"Dr. Alice" Case Study** (Section 6), demonstrating dynamic access blocking and remediation via MFA.
3.  **Vulnerability Analysis:** Demonstrates the **"Floating Trust Bug"** (Section 5.3) and verifies the **Just-in-Time (JIT)** fix.

## 📂 Project Structure

The directory structure maps directly to the sections of the paper:

```text
D-ABAC-Z_Simulation/
├── src/
│   ├── core/                   # [Section 3 & App B] Mathematical Kernels
│   │   ├── hmm_trust.py        # Hidden Markov Model belief updates (Eq. 3)
│   │   ├── decay_math.py       # Exponential decay logic (Eq. 4)
│   │   └── policy_lrap.py      # Risk-Adaptive Policy & Circuit Breaker (Eq. 6)
│   │
│   ├── components/             # [Fig 1] Zero Trust Architecture Components
│   │   ├── pep.py              # Policy Enforcement Point (Gateway)
│   │   ├── pdp.py              # Policy Decision Point (Logic Engine)
│   │   ├── pip.py              # Policy Information Point (Risk Context)
│   │   └── trust_engine.py     # Trust Engine (State Management & JIT)
│   │
│   ├── data/                   # [Section 6.3 & App C] Data & Calibration
│   │   ├── unsw_nb15_mapper.json # Likelihood Ratios derived from UNSW-NB15
│   │   └── config.py           # Global constants (Alpha=0.5, Lambda=0.05)
│   │
│   └── simulation/             # [Section 6 & 5.3] Reproducible Scripts
│       ├── scenario_alice.py   # Case Study: Hospital vs. Café
│       ├── reproduce_bug.py    # Counterexample: Stale Trust vs. JIT
│       └── benchmark_dos.py    # DoS Mitigation: Taylor Series Benchmark
│
└── formal_methods/             # [Section 4 & 5] Formal Verification Artifacts
    ├── z_spec/                 # LaTeX source for Z Notation Schemas
    └── alloy_model/            # .als source code for Model Checking
```

## 🚀 Getting Started

### Prerequisites
*   Python 3.9 or higher
*   (Optional) Alloy Analyzer 6.0 for running `.als` files.

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/D-ABAC-Z_Simulation.git
cd D-ABAC-Z_Simulation

# Install dependencies (numpy, pandas, etc.)
pip install -r requirements.txt
```

## 📊 Reproducing Paper Results

You can reproduce the specific experiments discussed in the paper using the CLI entry point:

```bash
python main.py
```

Or run individual simulation scripts as described below.

### 1. The "Dr. Alice" Case Study (Section 6.1)
Simulates a physician moving from a trusted Hospital network to an untrusted Public Café.

*   **Command:** `python -m src.simulation.scenario_alice`
*   **Expected Output:**
    *   `Time T=0`: Location **Hospital** ($\mathcal{R}=0.1$). Decision: **PERMIT**.
    *   `Time T=10`: Location **Café** ($\mathcal{R}=0.9$). Threshold spikes. Decision: **DENY**.
    *   `Time T=11`: Action **MFA Success**. Trust increases. Decision: **PERMIT** (Recovery).

### 2. The "Floating Trust Bug" & JIT Fix (Section 5.3)
Demonstrates the vulnerability found by Alloy where stale trust scores allow unauthorized access, and how the JIT calculation fixes it.

*   **Command:** `python -m src.simulation.reproduce_bug`
*   **Expected Output:**
    *   **V1 (Stale):** Access **GRANTED** (Incorrect - Vulnerability Reproduced).
    *   **V2 (JIT):** Access **DENIED** (Correct - Decay applied dynamically).

### 3. Performance & DoS Mitigation (Section 7.4 / Appendix E)
Benchmarks the CPU cost of the Exact Exponential Decay ($e^{-\lambda t}$) versus the Taylor Series Approximation ($1 - \lambda t$).

*   **Command:** `python -m src.simulation.benchmark_dos`
*   **Metric:** Execution time for 1,000,000 decay operations. Validates the $\mathcal{O}(1)$ efficiency claim.

## 🧩 Formal Methods Artifacts

The rigorous proofs mentioned in the paper are located in the `formal_methods/` directory.

*   **Z Notation:** `formal_methods/z_spec/main.tex` contains the `GlobalState`, `RequestAccess`, and `UpdateTrust` schemas.
*   **Alloy Models:** `formal_methods/alloy_model/dabac_z.als` contains the **Fixed-Point Arithmetic** mapping and the following assertions:
    *   `assert NoLeakage`
    *   `assert RiskMonotonicity`
    *   `assert ConditionalLiveness`

To verify these models, load the `.als` files into the [Alloy Analyzer](https://alloytools.org/).

## 📄 Citation

This paper is currently under submission to ESORICS 2026.

If you use this code or framework in your research, please cite:

```bibtex
@inproceedings{zhao2026dabacz,
  title={Formalizing Dynamic Trust: A Z-Based Specification and Alloy Verification of Context-Aware ABAC},
  author={Zhao, Xiaofei and Li, Zhipeng},
  booktitle={Proceedings of the 31st European Symposium on Research in Computer Security (ESORICS)},
  year={2026},
  note={Under Review}
}
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
