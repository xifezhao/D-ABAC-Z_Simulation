"""
Temporal Decay Functions
========================

This module implements the state transition logic for the HMM Trust Model.
In D-ABAC-Z, "Decay" is formally defined as the transition probability of 
remaining in the 'Honest' state over time interval Delta-t.

It supports two modes of calculation:
1. **Exact Mode**: Using transcendental exponential functions (Standard Model).
2. **Taylor Mode**: Using linear approximation for DoS mitigation (Appendix E).

Paper Reference:
    - Section 3.1: State Transitions (Eq. 4)
    - Appendix E.1: Taylor Series Approximation (Eq. 12)
    - Section 7.4: Algorithmic DoS Mitigation
"""

import math

# Default decay rate (Lambda) as used in Case Study
# Represents ~5% probability of state flipping per unit time
DEFAULT_LAMBDA = 0.05 

def calculate_time_delta(current_time: float, last_update_time: float) -> float:
    """
    Calculates Delta-t ensuring causality (non-negative time).
    
    Args:
        current_time: The timestamp of the current request.
        last_update_time: The timestamp stored in GlobalState.
        
    Returns:
        float: The elapsed time >= 0.
        
    Raises:
        ValueError: If current_time < last_update_time (Clock Skew/Error).
    """
    delta = current_time - last_update_time
    if delta < 0:
        # In a real distributed system, we might handle clock skew gracefully.
        # For formal verification, this is a violation of axioms.
        raise ValueError(f"Negative time delta detected: {delta}. Causality violation.")
    return delta

def decay_exact(
    trust_prior: float, 
    delta_t: float, 
    decay_rate: float = DEFAULT_LAMBDA
) -> float:
    """
    Implements the Exact Exponential Decay (The Standard Model).
    
    Formula (Eq. 4):
        tau(t) = tau(t-1) * e^(-lambda * delta_t)
        
    Use Case:
        - General purpose trust evaluation.
        - Scenarios where accuracy is paramount over CPU cycles.
    """
    if delta_t == 0:
        return trust_prior
        
    # The transcendental operation exp() is CPU intensive
    decay_factor = math.exp(-1.0 * decay_rate * delta_t)
    
    return trust_prior * decay_factor

def decay_taylor(
    trust_prior: float, 
    delta_t: float, 
    decay_rate: float = DEFAULT_LAMBDA
) -> float:
    """
    Implements the First-Order Taylor Approximation (DoS Mitigation).
    
    Formula (Eq. 12 / Appendix E.1):
        e^(-x) approx 1 - x
        tau(t) approx tau(t-1) * (1 - lambda * delta_t)
        
    Use Case:
        - High-throughput API Gateways (10k+ RPS).
        - Mitigating Algorithmic DoS attacks (Section 7.4).
        - Valid only when (lambda * delta_t) << 1.
    """
    if delta_t == 0:
        return trust_prior
        
    # O(1) arithmetic operation
    linear_factor = decay_rate * delta_t
    
    # Safety Check: Taylor approximation diverges for large steps.
    # If linear_factor > 1, trust becomes negative, which breaks probability axioms.
    if linear_factor >= 1.0:
        return 0.0
        
    return trust_prior * (1.0 - linear_factor)

def decay_hybrid(
    trust_prior: float, 
    delta_t: float, 
    decay_rate: float = DEFAULT_LAMBDA,
    threshold: float = 0.1
) -> float:
    """
    Implements the Hybrid Logic proposed in Appendix E.1.
    
    Logic:
        If the time step is small (error is negligible), use Fast Path (Taylor).
        If the time step is large (error accumulates), use Slow Path (Exact).
        
    Args:
        threshold (float): The value of (lambda * dt) below which Taylor is considered safe.
                           Derived from Lagrange remainder bounds.
    """
    # Check magnitude of the exponent
    x = decay_rate * delta_t
    
    if x < threshold:
        # Fast Path (Appendix E.1)
        return trust_prior * (1.0 - x)
    else:
        # Slow Path (Section 3.1)
        return trust_prior * math.exp(-1.0 * x)