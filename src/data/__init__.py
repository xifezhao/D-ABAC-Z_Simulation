"""
Data & Configuration Package
============================

This package manages the empirical data and global configuration constants used
to calibrate the D-ABAC-Z framework.

Mappings to Paper Sections:
---------------------------
1. **Global Constants** (Section 6.1):
   - Implemented in `config.py`.
   - Defines Alpha (Risk Sensitivity) and Lambda (Decay Rate).

2. **Data Calibration** (Section 6.3 & Appendix C.2):
   - Mappings for UNSW-NB15 Likelihood Ratios are stored in `unsw_nb15_mapper.json`.
   - Used to resolve the "Oracle Problem" by providing data-driven evidence values.

3. **Simulation Artifacts**:
   - `mock_db.json` provides the initial state for Case Studies.
"""

from .config import (
    ALPHA,
    LAMBDA,
    SCALE_K,
    TIME_UNIT_SCALE
)

# Define the public API
__all__ = [
    "ALPHA",
    "LAMBDA",
    "SCALE_K",
    "TIME_UNIT_SCALE"
]