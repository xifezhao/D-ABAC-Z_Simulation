"""
Linear Risk-Adaptive Policy (LRAP) Implementation
=================================================

This module implements the decision logic defined in **Section 3.2** of the paper.
It translates the abstract "Decision Inequality" into executable code.

Mathematical Definition:
------------------------
Access is granted if and only if:
    tau >= T_base * (1 + alpha * R_env)

Where:
    tau     : The effective trust score (after JIT decay).
    T_base  : The static base requirement of the object.
    alpha   : The Risk Sensitivity Coefficient.
    R_env   : The current environmental risk score.

Circuit Breaker (Lockdown):
---------------------------
If the calculated threshold > 1.0, the condition is mathematically unsatisfiable
(since tau <= 1.0). This represents the "Dynamic Lockdown" state discussed 
in the paper's "Safety-First" doctrine.
"""

from dataclasses import dataclass

@dataclass
class LRAPResult:
    """
    Structured output of a policy evaluation.
    
    Attributes:
        decision (bool): True if Access Permitted, False if Denied.
        threshold (float): The calculated dynamic threshold (Theta).
        is_lockdown (bool): True if the Circuit Breaker was triggered (Threshold > 1).
        reason (str): Human-readable explanation for the decision (for audit logs).
    """
    decision: bool
    threshold: float
    is_lockdown: bool
    reason: str

def calculate_threshold(
    base_requirement: float, 
    risk_score: float, 
    alpha: float
) -> float:
    """
    Calculates the Right-Hand Side (RHS) of the Decision Inequality.
    
    Formula (Eq. 6):
        Theta = T_base * (1 + alpha * R)
        
    Args:
        base_requirement (float): Intrinsic sensitivity of the object [0, 1].
        risk_score (float): Current environmental risk [0, 1].
        alpha (float): Risk sensitivity coefficient (e.g., 0.5).
        
    Returns:
        float: The required trust threshold. Can be > 1.0.
    """
    # Risk penalty factor
    risk_factor = 1.0 + (alpha * risk_score)
    
    return base_requirement * risk_factor

def evaluate_access(
    user_trust: float,
    base_requirement: float,
    risk_score: float,
    alpha: float = 0.5
) -> LRAPResult:
    """
    Evaluates the Linear Risk-Adaptive Policy (LRAP) inequality.
    
    Paper Reference:
        Section 3.2: The Decision Inequality (Eq. 6)
        Section 3.2: The "Dynamic Lockdown" Property
    
    Args:
        user_trust (float): The subject's current trust score (tau).
        base_requirement (float): Object's static requirement (T_base).
        risk_score (float): Environment's risk level (R_env).
        alpha (float): Sensitivity coefficient. Defaults to 0.5 (Case Study).
        
    Returns:
        LRAPResult: The decision decision and metadata.
    """
    # 1. Calculate the Dynamic Threshold (Theta)
    threshold = calculate_threshold(base_requirement, risk_score, alpha)
    
    # 2. Check for Circuit Breaker (Lockdown)
    # If required trust > 1.0, it is impossible to satisfy.
    if threshold > 1.0:
        return LRAPResult(
            decision=False,
            threshold=threshold,
            is_lockdown=True,
            reason=(
                f"DYNAMIC LOCKDOWN: Calculated threshold ({threshold:.2f}) exceeds 1.0. "
                f"Risk ({risk_score}) is too high for this asset."
            )
        )
        
    # 3. Evaluate the Inequality: tau >= Theta
    # Use strict comparison or allow slight epsilon for float matching?
    # Formal model says >=.
    if user_trust >= threshold:
        return LRAPResult(
            decision=True,
            threshold=threshold,
            is_lockdown=False,
            reason=(
                f"PERMIT: Trust ({user_trust:.2f}) meets risk-adaptive "
                f"threshold ({threshold:.2f})."
            )
        )
    else:
        return LRAPResult(
            decision=False,
            threshold=threshold,
            is_lockdown=False,
            reason=(
                f"DENY: Trust ({user_trust:.2f}) is insufficient for "
                f"threshold ({threshold:.2f}). Risk level: {risk_score}."
            )
        )