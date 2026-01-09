"""
Policy Enforcement Point (PEP)
==============================

This module implements the **Policy Enforcement Point**, acting as the gateway 
that intercepts Subject requests to Objects.

Architecture Mapping:
---------------------
- **Figure 1**: The central "PEP" block connecting Subject, Object, and PDP.
- **Section 7.5**: Implements the "Fast Path" architectural pattern where
  decisions are enforced based on cached policies to minimize latency.

Responsibilities:
1. Intercept access requests.
2. Delegate authorization logic to the PDP (Policy Decision Point).
3. Enforce the binary decision (Permit/Deny).
4. (Simulated) Emit access logs for the Asynchronous Trust Engine (Write-Behind).
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .pdp import PDP
from ..core.policy_lrap import LRAPResult

class PEP:
    """
    Simulates an API Gateway or Service Mesh Proxy (e.g., Envoy/Istio).
    """

    def __init__(self, pdp: PDP):
        """
        Args:
            pdp (PDP): Reference to the Policy Decision Point.
        """
        self.pdp = pdp
        # Simulated local cache for Section 7.6 "Trust Memoization"
        # Map: (subject_id, object_id) -> (decision, timestamp)
        self._decision_cache: Dict[str, Any] = {}

    def access_request(
        self, 
        subject_id: str, 
        object_id: str, 
        env_context: Dict[str, Any],
        use_cache: bool = False
    ) -> Dict[str, Any]:
        """
        Handles an incoming access request from a Subject.

        Mapping to Paper:
            - **Figure 1, Arrow 1**: Request (Subject -> PEP)
            - **Figure 1, Arrow 2**: Query (PEP -> PDP)
            - **Figure 1, Arrow 5**: Permit/Deny (PDP -> PEP)
            - **Figure 1, Arrow 6**: Access (PEP -> Object)

        Args:
            subject_id: Unique ID of the user/device.
            object_id: Unique ID of the resource.
            env_context: Dictionary containing environmental attributes (e.g., IP, Time).
            use_cache: If True, enables the "Micro-caching" optimization (Section 7.6).

        Returns:
            Dict: A structured response mimicking an HTTP 200/403 response.
        """
        request_time = datetime.now()
        
        # --- 1. Cache Lookup (Optimization / Gap Analysis) ---
        if use_cache:
            cache_key = f"{subject_id}::{object_id}"
            cached_entry = self._decision_cache.get(cache_key)
            if cached_entry:
                # In a real system, we would check TTL here (epsilon window)
                # Section 7.6: "Trust Memoization"
                return self._enforce(cached_entry['result'], "Cached Decision")

        # --- 2. Delegate to PDP (The Z-Spec Logic) ---
        # Corresponds to the synchronous decision phase described in Appendix E.2
        decision_result: LRAPResult = self.pdp.decide(subject_id, object_id, env_context)

        # --- 3. Cache Update ---
        if use_cache:
            self._decision_cache[f"{subject_id}::{object_id}"] = {
                'result': decision_result,
                'time': request_time
            }

        # --- 4. Asynchronous Write-Behind (Simulated) ---
        # Section 7.5: "Access logs are pushed to a durable message queue..."
        # In this simulation, we assume the Trust Engine observes this event 
        # via the PDP side-channel or log ingestion.
        self._emit_audit_log(subject_id, object_id, decision_result)

        # --- 5. Enforcement ---
        return self._enforce(decision_result, "Live Calculation")

    def _enforce(self, result: LRAPResult, source: str) -> Dict[str, Any]:
        """
        Constructs the final response based on the LRAPResult.
        """
        status_code = 200 if result.decision else 403
        status_msg = "ACCESS GRANTED" if result.decision else "ACCESS DENIED"
        
        return {
            "status": status_code,
            "message": status_msg,
            "source": source,
            "details": {
                "threshold": round(result.threshold, 4),
                "reason": result.reason,
                "lockdown_active": result.is_lockdown
            }
        }

    def _emit_audit_log(self, s: str, o: str, res: LRAPResult):
        """Simulates pushing to Kafka/Splunk."""
        # This function is a placeholder for the side-effect 
        # that drives the feedback loop (Arrow 0 in Fig 1).
        pass