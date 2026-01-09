"""
Trust Engine
============

This module implements the **Trust Engine**, responsible for maintaining the 
probabilistic belief state of all subjects.

Architecture Mapping:
---------------------
- **Figure 1**: The "Trust Engine" block executing HMM updates and Decay.
- **Section 4.1**: Maintains the `GlobalState` (Trust Scores + Timestamps).
- **Section 5.3**: Implements **Just-in-Time (JIT)** evaluation to fix the 
  "Floating Trust Bug".
- **Appendix B.3**: Implements the `UpdateTrust` Z Schema logic.

Responsibilities:
1. Store persistent trust states ($\tau_{stored}$) and timestamps ($T_{last}$).
2. Calculate effective trust ($\tau_{effective}$) on demand (Read Path).
3. Process behavioral evidence to update state (Write Path).
"""

import time
from typing import Dict, Any
from datetime import datetime
from ..core.decay_math import decay_exact, calculate_time_delta
from ..core.hmm_trust import calculate_posterior
from ..data.config import LAMBDA

class TrustEngine:
    """
    Manages the lifecycle of Trust Scores using HMM semantics.
    """

    def __init__(self):
        # Simulated In-Memory Database (The GlobalState Schema)
        # Structure: { subject_id: {'score': float, 'last_update': float} }
        self._db: Dict[str, Dict[str, Any]] = {}
        
        # Seed Dr. Alice for the Case Study (Section 6.1)
        # Initial Trust = 0.75
        self._seed_data()

    def _seed_data(self):
        """Initializes the DB with Dr. Alice's baseline state."""
        self._db["alice"] = {
            "score": 0.75,
            "last_update": time.time()
        }

    def get_effective_trust(self, subject_id: str) -> float:
        """
        Retrieves the *current* effective trust score for a subject.
        
        CRITICAL LOGIC: Just-in-Time (JIT) Evaluation
        ---------------------------------------------
        Paper Reference: Section 5.3 (Refinement of Z Spec).
        
        Instead of returning the stored value directly, this method calculates
        what the trust *should* be right now based on the time elapsed since
        the last update.
        
        Formula:
            tau_effective = decay(tau_stored, current_time - last_update_time)
            
        Args:
            subject_id: The unique ID of the subject.
            
        Returns:
            float: The time-decayed trust score [0, 1].
        """
        state = self._db.get(subject_id)
        
        # Default assumption for unknown subjects:
        # Start with low trust (e.g., 0.1) or neutral (0.5) depending on policy.
        # For Zero Trust, we default to 0.0 or a low initial bootstrap value.
        if not state:
            return 0.0
            
        stored_trust = state["score"]
        last_update_ts = state["last_update"]
        
        # 1. Calculate Delta-t
        current_time = time.time()
        delta_t = calculate_time_delta(current_time, last_update_ts)
        
        # 2. Apply JIT Decay (Read-Only operation)
        # We do NOT update the DB here. This preserves the "Last Evidence Time".
        effective_trust = decay_exact(stored_trust, delta_t, LAMBDA)
        
        return effective_trust

    def process_evidence(self, subject_id: str, evidence_likelihood: float):
        """
        Updates the subject's trust state based on new behavioral evidence.
        
        Paper Reference: Section 4.4 / Appendix B.3 (UpdateTrust Schema).
        
        Logic Flow:
            1. Predict: Apply decay to align prior to current time.
            2. Update: Apply Bayesian inference with new evidence.
            3. Commit: Write new score and timestamp to DB.
            
        Args:
            subject_id: The unique ID of the subject.
            evidence_likelihood: The likelihood ratio P(E|H) of the observed event.
                                 (Derived from UNSW-NB15 in real scenarios).
        """
        state = self._db.get(subject_id)
        if not state:
            # Bootstrap new user
            state = {"score": 0.5, "last_update": time.time()}
        
        stored_trust = state["score"]
        last_update_ts = state["last_update"]
        current_time = time.time()
        
        # --- Step 1: Prediction (Decay) ---
        delta_t = calculate_time_delta(current_time, last_update_ts)
        prior_decayed = decay_exact(stored_trust, delta_t, LAMBDA)
        
        # --- Step 2: Update (Bayes) ---
        # Eq. 3: Posterior = (L * Prior) / Margin
        # Assuming P(E|~H) is inverse or fixed (simplified for simulation)
        # For the simulation, we use the core function which handles the math.
        # In a real system, likelihood_compromised might come from a threat model.
        posterior = calculate_posterior(
            prior=prior_decayed,
            likelihood_honest=evidence_likelihood,
            likelihood_compromised=0.001 if evidence_likelihood > 1 else 0.999 
            # Heuristic: if evidence is good (L>1), prob of seeing it from attacker is low.
        )
        
        # --- Step 3: Commit (State Transition) ---
        self._db[subject_id] = {
            "score": posterior,
            "last_update": current_time
        }
        
        # Logging for the simulation trace
        print(f"[TrustEngine] Updated {subject_id}: "
              f"Prior({stored_trust:.2f}) -> Decay({prior_decayed:.2f}) -> "
              f"Evidence(L={evidence_likelihood}) -> Posterior({posterior:.2f})")

    # --- Debugging / Simulation Helpers ---
    
    def set_trust_manually(self, subject_id: str, score: float):
        """Helper to force a state for Scenario reproduction."""
        self._db[subject_id] = {
            "score": score,
            "last_update": time.time()
        }