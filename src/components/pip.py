"""
Policy Information Point (PIP)
==============================

This module implements the **Policy Information Point**, responsible for 
providing the environmental context and attribute values to the PDP.

Architecture Mapping:
---------------------
- **Figure 1**: The "PIP" block feeding Risk and Attributes into the PDP.
- **Section 3.2**: Implements the Risk Aggregation Function (Eq. 5).
- **Section 6.1**: Provides the specific scenarios (Hospital vs. Café).

Responsibilities:
1. Normalize raw context data into a scalar Risk Score $\mathcal{R}_{env} \in [0, 1]$.
2. Provide Object metadata (specifically Base Trust Requirement $\mathcal{T}_{base}$).
"""

from typing import Dict, Any

class PIP:
    """
    Simulates an Attribute Provider and Risk Engine.
    In a real system, this would query IDP (LDAP/AD) and Threat Intel feeds.
    """

    def __init__(self):
        # Simulated database for Object Metadata
        # Corresponds to Section 6.1 Setup Parameters
        self._object_db = {
            "record_8842": {
                "type": "PHR",
                "classification": "high",
                # The intrinsic sensitivity T_base(o)
                "base_trust_requirement": 0.60 
            },
            "public_page": {
                "type": "HTML",
                "classification": "public",
                "base_trust_requirement": 0.0
            }
        }

    def get_object_metadata(self, object_id: str) -> Dict[str, Any]:
        """
        Retrieves static attributes for a requested resource.
        """
        return self._object_db.get(object_id, {
            "type": "unknown", 
            "base_trust_requirement": 1.0 # Fail-safe: unknown objects require max trust
        })

    def get_environmental_risk(self, context: Dict[str, Any]) -> float:
        """
        Calculates the aggregate Environmental Risk score $\mathcal{R}_{env}$.

        Paper Reference:
            Section 3.2, Equation (5): R = min(1, sum(w_i * phi(c_i)))

        In this simulation, we map specific logical locations to the 
        pre-calculated risk values used in the Case Study (Section 6.1).

        Args:
            context (dict): Raw environment data (e.g., {'location': 'hospital'}).

        Returns:
            float: A value between 0.0 (Safe) and 1.0 (Hostile).
        """
        location = context.get("location", "unknown").lower()
        network_security = context.get("network_security", "none")

        # --- Scenario A: Hospital Network (Section 6.1) ---
        # Managed Intranet + IDS present
        if location == "hospital" or network_security == "wpa3_enterprise":
            return 0.1

        # --- Scenario B: Public Café (Section 6.1) ---
        # Open Wi-Fi + Unmanaged location
        if location == "cafe" or network_security == "open":
            return 0.9

        # --- Default / Fallback ---
        # Assume medium-high risk for unknown contexts (Zero Trust Default)
        return 0.5