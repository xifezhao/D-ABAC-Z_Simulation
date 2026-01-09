"""
Global Configuration Constants
==============================

This module defines the tunable parameters for the D-ABAC-Z framework.
The values are strictly calibrated to match the setup parameters described 
in **Section 6.1 (Case Study)** of the paper to ensure reproducibility.

Paper References:
    - **Section 3.2**: `ALPHA` (Risk Sensitivity Coefficient)
    - **Section 3.1**: `LAMBDA` (HMM State Transition / Decay Rate)
    - **Section 5.1**: `SCALE_K` (Fixed-Point Scaling Factor for Verification)
"""

# --- Policy Parameters (Section 6.1) ---

# Risk Sensitivity Coefficient (alpha)
# Determines how aggressively the required trust threshold rises 
# in response to environmental risk.
# Formula: Threshold = T_base * (1 + ALPHA * R_env)
#
# A value of 0.5 means a max-risk environment (R=1.0) increases
# the requirement by 50%.
ALPHA: float = 0.5

# Trust Decay Rate (lambda)
# Represents the probability of a user transitioning from 'Honest' to 
# 'Compromised' per unit of time.
# Formula: tau_new = tau_old * e^(-LAMBDA * dt)
#
# Value 0.05 implies roughly 5% confidence loss per time unit.
LAMBDA: float = 0.05

# --- Verification Parameters (Section 5.1 / Appendix D) ---

# Fixed-Point Scaling Factor (K)
# Used to simulate the Alloy Analyzer's discrete logic within Python.
# Maps continuous probabilities [0, 1] to integers [0, K].
#
# K=10 allows representing decimal precision down to 0.1 (e.g., 0.5 -> 5).
# This matches the "Scope" parameters used in the paper's Model Checking.
SCALE_K: int = 10

# --- Simulation Runtime Helpers ---

# Time Unit Scale
# Defines what "1.0" delta_t represents in real-world seconds for the demo.
# Default: 1 simulation unit = 1 second.
TIME_UNIT_SCALE: float = 1.0