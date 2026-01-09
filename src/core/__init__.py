"""
Core Mathematical Kernels
=========================

This package implements the pure mathematical logic defined in **Section 3** 
of the paper. It is free of side effects and external system dependencies (IO), 
making it suitable for rigorous unit testing and verification.

Mappings to Paper Equations:
----------------------------
1. **HMM Belief Update** (Section 3.1, Eq. 3)
   -> Implemented in `hmm_trust.calculate_posterior`
   
2. **Trust Decay / State Transition** (Section 3.1, Eq. 4)
   -> Implemented in `decay_math.decay_exact`
   -> Taylor Approximation (App E.1) in `decay_math.decay_taylor`

3. **Linear Risk-Adaptive Policy (LRAP)** (Section 3.2, Eq. 6)
   -> Implemented in `policy_lrap.evaluate_access`
   -> Circuit Breaker logic (Section 3.2) in `policy_lrap`

"""

from .hmm_trust import (
    TrustBeliefState, 
    calculate_posterior
)

from .decay_math import (
    decay_exact,
    decay_taylor,
    calculate_time_delta
)

from .policy_lrap import (
    LRAPResult,
    calculate_threshold,
    evaluate_access
)

# Define the public API of the core module
__all__ = [
    # HMM Logic
    "TrustBeliefState",
    "calculate_posterior",
    
    # Decay Logic
    "decay_exact",
    "decay_taylor",
    "calculate_time_delta",
    
    # Policy Logic
    "LRAPResult",
    "calculate_threshold",
    "evaluate_access",
]