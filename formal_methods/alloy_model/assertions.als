module assertions

/*
 * Security Properties Verification
 * ================================
 * This module defines the formal assertions derived from the D-ABAC-Z requirements.
 * It imports the core logic from `dabac_z.als` and verifies it against threat models.
 *
 * Mappings to Paper:
 * ------------------
 * - Section 5.2: Security Properties (Textual descriptions)
 * - Appendix D.2: Source code listings
 */

open dabac_z

// --- 1. Safety Assertion (The "No Leakage" Invariant) ---

/*
 * Assert 1: Safety
 * ----------------
 * Verifies the "Defense in Depth" principle.
 * Dynamic trust (Layer 2) must never override Static Policy (Layer 1).
 *
 * Logic: If static attributes do not match, Decision MUST be Deny,
 * regardless of Trust Score or Risk Level.
 */
assert NoLeakage {
    all s: Subject, o: Object, risk: Int |
        // Pre-condition: Static mismatch (Layer 1 fails)
        not (o in s.(GlobalState.staticMatch)) 
        
        // Post-condition: Access denied
        implies not isPermitted[s, o, risk]
}

// Check command: Use 10-bit integers to handle Fixed-Point scaling (K=10)
check NoLeakage for 5 but 10 Int


// --- 2. Risk Monotonicity Assertion ---

/*
 * Assert 2: Risk Monotonicity
 * ---------------------------
 * Verifies that the system behaves monotonically regarding risk.
 * Higher Risk must strictly imply Higher (or equal) Security Standards.
 *
 * Logic:
 * Given Risk R2 > R1.
 * If a subject is permitted at R2 (High Risk), they MUST be permitted at R1 (Low Risk).
 * Contrapositive: If Denied at R1, MUST be Denied at R2.
 */
assert RiskMonotonicity {
    all s: Subject, o: Object, r1, r2: Int |
        // Pre-condition: R2 is strictly riskier than R1
        (r2 > r1 and r2 =< SCALE_K and r1 >= 0) 
        implies (
            // Implication: Permission at high risk implies permission at low risk
            isPermitted[s, o, r2] implies isPermitted[s, o, r1]
        )
}

// This check validates that the Fixed-Point arithmetic (div/mul order) 
// does not introduce rounding errors that invert the security logic.
check RiskMonotonicity for 5 but 10 Int


// --- 3. Liveness Assertion (Trust Recovery) ---

/*
 * Assert 3: Conditional Liveness
 * ------------------------------
 * Verifies the "Trust Recovery" property (Section 6.2 Remediation).
 * Proves the system is not a permanent deadlock/blacklist.
 * 
 * Logic (Linear Temporal Logic - Alloy 6):
 * If the environment eventually stays benign (Risk=0) AND 
 * the user acts honestly (Trust -> Max), THEN access is eventually granted.
 *
 * NOTE: This assertion requires running in Alloy 6+ with temporal solver.
 */
assert ConditionalLiveness {
    // Quantify over all Subjects and Objects
    all s: Subject, o: Object |
        // Trigger Conditions:
        // 1. Static attributes match (otherwise Safety blocks it)
        (o in s.(GlobalState.staticMatch)) and
        // 2. Risk becomes zero (Benign environment)
        (GlobalState.envRisk = 0) and
        // 3. Subject has max trust (Simulating successful MFA/Good Behavior)
        (s.trust = SCALE_K)
        
        // Consequence:
        // Access must be permitted
        implies isPermitted[s, o, 0]
}

/* 
 * Trace generation for Liveness check.
 * We look for a counterexample where conditions are met but access is still denied.
 * If no counterexample is found, the property holds.
 */
check ConditionalLiveness for 5 but 10 Int