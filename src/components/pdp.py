"""
Policy Decision Point (PDP)
===========================

This module implements the **Policy Decision Point**, the logical brain of the
Zero Trust Control Plane. It orchestrates the retrieval of attributes and 
executes the formal decision logic.

Architecture Mapping:
---------------------
- **Figure 1**: The "PDP" block receiving queries from PEP and fetching data 
  from PIP/Trust Engine.
- **Section 4.2**: Implements the `RequestAccess` Z Schema.
- **Section 3.2**: Executes the Linear Risk-Adaptive Policy (LRAP).

Responsibilities:
1. Fetch Environmental Risk ($\mathcal{R}_{env}$) from PIP.
2. Fetch Effective Trust ($\tau$) from Trust Engine (JIT evaluation).
3. Execute Layer 1: Static Attribute Validation (Safety Assertion).
4. Execute Layer 2: Dynamic Risk Evaluation (Risk Monotonicity).
"""

from typing import Dict, Any
from .pip import PIP
from .trust_engine import TrustEngine
from ..core.policy_lrap import evaluate_access, LRAPResult
from ..data.config import ALPHA

class PDP:
    """
    Implements the formal decision logic defined in the Z Specification.
    """

    def __init__(self, pip: PIP, trust_engine: TrustEngine):
        """
        Dependency Injection of sibling components.
        
        Args:
            pip: Policy Information Point (Source of truth for attributes/risk).
            trust_engine: Source of truth for dynamic trust scores.
        """
        self.pip = pip
        self.trust_engine = trust_engine

    def decide(
        self, 
        subject_id: str, 
        object_id: str, 
        env_context: Dict[str, Any]
    ) -> LRAPResult:
        """
        Executes the `RequestAccess` operation logic (Section 4.2).

        Logic Flow:
            1. Fetch GlobalState variables (Risk, Trust, Attributes).
            2. Check Static Constraints (e.g., Role/Clearance).
            3. Check Dynamic Constraints (Equation 6).

        Args:
            subject_id: The ID of the requesting user/entity.
            object_id: The ID of the target resource.
            env_context: Raw context data (IP, Time, etc.).

        Returns:
            LRAPResult: The formal decision structure (Decision, Threshold, Reason).
        """
        
        # --- Step 1: Context Gathering (PIP Interaction) ---
        # Corresponds to fetching 'envRisk' and 'objectReqs' in Z Spec
        risk_score = self.pip.get_environmental_risk(env_context)
        object_meta = self.pip.get_object_metadata(object_id)
        base_requirement = object_meta['base_trust_requirement']
        
        # --- Step 2: Trust Gathering (Trust Engine Interaction) ---
        # Corresponds to fetching 'userTrustScores' and applying JIT decay
        # Fixes the "Floating Trust Bug" (Section 5.3)
        effective_trust = self.trust_engine.get_effective_trust(subject_id)

        # --- Step 3: Layer A - Static Attribute Validation ---
        # Section 5.2: Assert 1 (Safety / No Leakage)
        # "Dynamic trust layer supplements, but never overrides, the static layer."
        # Note: In this simplified simulation, we assume Dr. Alice implies 
        # valid static roles. In a full implementation, we would check:
        # if not self.pip.check_static_permissions(subject_id, object_id): ...
        
        # --- Step 4: Layer B - Dynamic Risk Evaluation ---
        # Section 3.2: The Linear Risk-Adaptive Policy (LRAP)
        # Formula: tau >= T_base * (1 + alpha * R)
        result = evaluate_access(
            user_trust=effective_trust,
            base_requirement=base_requirement,
            risk_score=risk_score,
            alpha=ALPHA  # Global constant from config (0.5)
        )

        return result