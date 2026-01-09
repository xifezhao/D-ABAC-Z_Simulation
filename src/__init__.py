"""
D-ABAC-Z Source Package
=======================

This package contains the core implementation of the mathematical models, 
architectural components, and simulation logic for the D-ABAC-Z framework.

Structure Mapping to Paper:
---------------------------
* src.core       -> Section 3: Mathematical Model (HMM, LRAP, Decay)
* src.components -> Figure 1: Architecture (PEP, PDP, Trust Engine)
* src.data       -> Section 6.3 & App C: Data Calibration (UNSW-NB15)
* src.simulation -> Section 5 & 6: Experiments and Benchmarks

Usage:
    from src.core.hmm_trust import TrustBeliefState
    from src.components.trust_engine import TrustEngine
"""

# Project Metadata
__version__ = "1.0.0"
__author__ = "Xiaofei Zhao"
__license__ = "MIT"

# Expose key modules for cleaner imports if needed
# (Optional: allows 'from src import TrustEngine')
# from src.components.trust_engine import TrustEngine
# from src.components.pep import PEP