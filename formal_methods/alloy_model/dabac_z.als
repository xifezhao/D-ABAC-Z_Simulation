module dabac_z

/*
 * D-ABAC-Z Core Model
 * ===================
 * This module defines the structural model and decision logic for the D-ABAC-Z framework.
 * It implements the "Fixed-Point Arithmetic" mapping to verify the Linear Risk-Adaptive Policy.
 *
 * Mappings to Paper:
 * ------------------
 * - Section 5.1: Mapping Z to Alloy (Fixed-Point Strategy)
 * - Appendix D.1: Implementation details of scaling factors
 * - Equation (9): The integer-based decision inequality
 */

open util/integer

// --- 1. Configuration Constants ---

// Global Scaling Factor (K)
// Maps continuous probability [0.0, 1.0] to discrete integers [0, K].
// A value of 10 allows representing 0.1 increments.
// NOTE: When running this, ensure Alloy 'Int' scope is set to at least 5 bits (-16..15) 
// or higher depending on calculations.
let SCALE_K = 10 

// Risk Sensitivity Coefficient (Alpha)
// In paper, Alpha = 0.5.
// In Fixed-Point (scaled by K=10), Alpha = 5.
let ALPHA_FIXED = 5

// --- 2. Signatures (Type Definitions) ---

sig Subject {
    // Represents the user's effective trust score (tau).
    // In JIT model, this is the value *after* decay calculation.
    trust: one Int
} {
    // Invariant: Trust must be within probability bounds [0, 1] -> [0, K]
    trust >= 0 
    trust =< SCALE_K
}

sig Object {
    // Represents the intrinsic base trust requirement (T_base).
    baseReq: one Int
} {
    // Invariant: Requirement must be positive and normalized
    baseReq >= 0 
    baseReq =< SCALE_K
}

one sig GlobalState {
    // Current Environmental Risk (R_env).
    // 0 = Safe, K = Hostile.
    envRisk: one Int,
    
    // Static Attribute Matching (Layer A)
    // Maps Subjects to Objects they have "Role" access to.
    staticMatch: Subject -> Object
} {
    // Invariant: Risk must be within bounds [0, 1] -> [0, K]
    envRisk >= 0 
    envRisk =< SCALE_K
}

// --- 3. Core Decision Logic (The LRAP Predicate) ---

/*
 * isPermitted
 * -----------
 * Implements the Linear Risk-Adaptive Policy (LRAP) inequality using Fixed-Point Math.
 * 
 * Paper Equation (9):
 *      tau_fix >= T_fix + (T_fix * alpha_fix * R_fix) / K^2
 *
 * Logic:
 *      1. Check Static Attributes (Safety Layer).
 *      2. Calculate Dynamic Threshold (Risk Layer).
 *      3. Compare Trust vs Threshold.
 */
pred isPermitted[s: Subject, o: Object, risk: Int] {
    // --- Layer 1: Static Attribute Check ---
    // Corresponds to Assert 1 (Safety)
    o in s.(GlobalState.staticMatch)

    // --- Layer 2: Dynamic Trust Check ---
    let t = s.trust
    let b = o.baseReq
    
    // Step A: Calculate the Risk Penalty
    // We multiply FIRST to preserve precision (avoiding "Discretization Fallacy").
    // Units: K * K * K = K^3
    let numerator = mul[b, mul[ALPHA_FIXED, risk]]
    
    // Step B: Normalize back to scale K
    // Divisor: K * K
    let denominator = mul[SCALE_K, SCALE_K]
    
    // Penalty = (Base * Alpha * Risk) / K^2
    let penalty = div[numerator, denominator]
    
    // Step C: The Decision Inequality
    // Trust >= Base + Penalty
    t >= add[b, penalty]
}

// --- 4. Helper Predicates for Trace Generation ---

/*
 * updateTrust
 * -----------
 * Simulates the effect of the 'UpdateTrust' operation.
 * Used in dynamic traces to verify Liveness.
 * 
 * Args:
 *   s: Subject
 *   newVal: The new trust value (result of HMM update)
 */
pred setTrust[s: Subject, newVal: Int] {
    // Pre-condition: Value is valid
    newVal >= 0 and newVal =< SCALE_K
    // Post-condition: Trust is updated
    s.trust = newVal
}

/*
 * setRisk
 * -------
 * Simulates a change in environment.
 */
pred setRisk[newRisk: Int] {
    newRisk >= 0 and newRisk =< SCALE_K
    GlobalState.envRisk = newRisk
}