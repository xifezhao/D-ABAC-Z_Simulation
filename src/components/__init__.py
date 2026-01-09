"""
Zero Trust Architecture Components
==================================

This package implements the logical components of the Zero Trust Control Plane,
strictly following the architecture defined in **Figure 1** of the paper.

Component Mapping:
------------------
1. **PEP (Policy Enforcement Point)**:
   - Implemented in `pep.py`.
   - Acts as the gateway intercepting access requests.
   - Corresponds to the central "PEP" block in Fig 1.

2. **PDP (Policy Decision Point)**:
   - Implemented in `pdp.py`.
   - Orchestrates the decision process by querying PIP and Trust Engine.
   - Executes the Z-Spec logic (Section 4.2).

3. **PIP (Policy Information Point)**:
   - Implemented in `pip.py`.
   - Provides environmental context (Risk) and static attributes.
   - Corresponds to the "PIP" block in Fig 1.

4. **Trust Engine**:
   - Implemented in `trust_engine.py`.
   - Manages the dynamic state (GlobalState) and HMM beliefs.
   - Handles the "Feedback Loop" (Step 0 in Fig 1) and JIT calculations.
"""

from .pep import PEP
from .pdp import PDP
from .pip import PIP
from .trust_engine import TrustEngine

__all__ = [
    "PEP",
    "PDP",
    "PIP",
    "TrustEngine"
]