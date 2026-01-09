"""
Hidden Markov Model (HMM) Trust Logic
=====================================

This module implements the probabilistic semantics defined in **Section 3.1** of the paper.
It treats "Trust" not as a heuristic score, but as the **Belief State** of an HMM.

Mathematical Definition:
------------------------
Let H_t be the hidden state {Honest, Compromised}.
The Trust Score tau(t) is the posterior probability:
    tau(t) = P(H_t = Honest | Evidence_1:t)

The update follows the Recursive Bayesian Filter (Equation 3):
    tau_post = (P(E|H) * tau_prior) / P(E)

Where P(E) is the marginal likelihood:
    P(E) = P(E|H)*tau_prior + P(E|~H)*(1 - tau_prior)
"""

from dataclasses import dataclass
import numpy as np

# Precision tolerance for floating point comparisons
EPSILON = 1e-9

@dataclass
class TrustBeliefState:
    """
    Represents the subjective probability tau in [0, 1].
    
    Attributes:
        value (float): The current probability P(H=Honest).
    """
    value: float

    def __post_init__(self):
        """Enforces the probability axiom: 0 <= p <= 1."""
        if not (0.0 - EPSILON <= self.value <= 1.0 + EPSILON):
            raise ValueError(f"Trust score {self.value} is out of probability bounds [0, 1]")
        # Clamp for numerical stability
        self.value = max(0.0, min(1.0, self.value))

def calculate_posterior(
    prior: float, 
    likelihood_honest: float, 
    likelihood_compromised: float = 0.5
) -> float:
    """
    Performs the Bayesian Update step (Emission Update).
    
    Paper Reference:
        Section 3.1, Equation (3)
        Appendix B.2 (BayesStep)

    Args:
        prior (float): The current trust score tau(t-1) (after decay).
        likelihood_honest (float): P(E | H=Honest). Probability of observing evidence E 
                                   given the user is Honest. Derived from UNSW-NB15 "Normal".
        likelihood_compromised (float): P(E | H=Compromised). Probability of observing evidence E
                                        given the user is Compromised. Derived from UNSW-NB15 "Attack".
                                        Defaults to 0.5 (Maximum Entropy) if unknown.

    Returns:
        float: The posterior trust score tau(t).
    """
    
    # 1. Calculate Numerator: P(E|H) * P(H)
    numerator = likelihood_honest * prior
    
    # 2. Calculate Marginal Likelihood (Denominator): P(E)
    # P(E) = P(E|H)P(H) + P(E|~H)P(~H)
    prob_compromised = 1.0 - prior
    denominator = (likelihood_honest * prior) + (likelihood_compromised * prob_compromised)
    
    # 3. Handle numerical edge cases (Avoid Div/0)
    if denominator < EPSILON:
        # If P(E) is 0, this event is impossible under current model. 
        # In a robust system, we shouldn't update, or result is undefined.
        # Returning prior is a fail-safe.
        return prior
        
    posterior = numerator / denominator
    
    return posterior

def calculate_evidence_strength(likelihood_honest: float, likelihood_compromised: float) -> float:
    """
    Helper to calculate the Log Likelihood Ratio (LLR), used in some Z specifications 
    to represent 'evidence' as a scalar.
    
    LLR = log( P(E|H) / P(E|~H) )
    """
    if likelihood_compromised == 0:
        return float('inf')
    if likelihood_honest == 0:
        return float('-inf')
        
    return np.log(likelihood_honest / likelihood_compromised)