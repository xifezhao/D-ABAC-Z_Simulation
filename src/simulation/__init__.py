"""
Simulation Scenarios Package
============================

This package contains the executable scripts required to reproduce the 
experimental results and case studies described in the paper.

Scenario Mapping:
-----------------
1. **Case Study: Dr. Alice** (Section 6.1 & 6.2)
   - Module: `scenario_alice.py`
   - Goal: Demonstrate context-aware access control (Permit -> Deny -> Recover).
   - Verifies: Risk Monotonicity & Liveness assertions.

2. **Vulnerability Analysis** (Section 5.3)
   - Module: `reproduce_bug.py`
   - Goal: Demonstrate the "Floating Trust Bug" caused by state stagnation.
   - Verifies: The effectiveness of the Just-in-Time (JIT) refinement.

3. **Performance Benchmark** (Section 7.4 & Appendix E)
   - Module: `benchmark_dos.py`
   - Goal: Measure the CPU cost of trust decay calculations.
   - Verifies: The validity of the Taylor Series Approximation for DoS mitigation.
"""

from . import scenario_alice
from . import reproduce_bug
from . import benchmark_dos

__all__ = [
    "scenario_alice",
    "reproduce_bug",
    "benchmark_dos"
]