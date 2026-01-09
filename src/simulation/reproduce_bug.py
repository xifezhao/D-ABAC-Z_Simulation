"""
Vulnerability Analysis: The "Floating Trust Bug"
================================================

This script reproduces the critical vulnerability discovered by the Alloy Analyzer
in **Section 5.3** and **Appendix D.3**.

The Scenario:
-------------
1. User logs in with High Trust (0.9).
2. User goes inactive for a long period (Delta-t = 30 units).
   - Mathematical Truth: Trust should decay to ~0.20.
   - V1 System (Stale): Retains 0.9 because no write-event occurred.
   - V2 System (JIT): Calculates 0.20 on-the-fly.
3. Environmental Risk spikes (0.1 -> 0.8).
   - Required Threshold rises to 0.84.
4. User requests access.

Expected Outcome:
-----------------
- **V1 (Stale):** 0.9 >= 0.84 -> PERMIT (Security Violation / False Negative).
- **V2 (Fixed):** 0.20 < 0.84 -> DENY (Correct / Safe).
"""

import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich import box

from ..core.decay_math import decay_exact
from ..core.policy_lrap import evaluate_access
from ..data import config

console = Console()

class V1_StaleSystem:
    """
    Simulates the flawed architecture where trust is only updated on write events.
    Corresponds to the initial Z specification before refinement.
    """
    def __init__(self, initial_trust):
        self.stored_trust = initial_trust
        
    def get_trust(self, delta_t):
        # THE BUG: Ignores delta_t because no "event" triggered an update.
        # Returns the stale stored value.
        return self.stored_trust

class V2_JITSystem:
    """
    Simulates the D-ABAC-Z architecture with Just-in-Time evaluation.
    Corresponds to the refined Z specification (Section 4.2).
    """
    def __init__(self, initial_trust):
        self.stored_trust = initial_trust
        
    def get_trust(self, delta_t):
        # THE FIX: Applies decay dynamically on read.
        return decay_exact(self.stored_trust, delta_t, config.LAMBDA)

def run():
    console.clear()
    console.rule("[bold red]Vulnerability Reproduction: Floating Trust Bug[/bold red]")
    
    # --- Parameters ---
    initial_trust = 0.90
    t_base = 0.60
    
    # Time elapsed (in simulation units)
    # With Lambda=0.05, 30 units should decay 0.9 -> ~0.2
    delta_t = 30.0 
    
    # Risk Spike
    risk_high = 0.8 
    
    console.print(f"Initial Trust: [bold]{initial_trust}[/bold]")
    console.print(f"Elapsed Time:  [bold]{delta_t}[/bold] units")
    console.print(f"Current Risk:  [bold]{risk_high}[/bold] (Critical)")
    console.print(f"Decay Rate:    {config.LAMBDA}")
    console.print()

    # --- Initialize Systems ---
    sys_v1 = V1_StaleSystem(initial_trust)
    sys_v2 = V2_JITSystem(initial_trust)

    # --- Execution ---
    
    # 1. Get Effective Trust
    trust_v1 = sys_v1.get_trust(delta_t)
    trust_v2 = sys_v2.get_trust(delta_t)
    
    # 2. Evaluate Policy
    # Threshold = 0.6 * (1 + 0.5 * 0.8) = 0.6 * 1.4 = 0.84
    result_v1 = evaluate_access(trust_v1, t_base, risk_high, config.ALPHA)
    result_v2 = evaluate_access(trust_v2, t_base, risk_high, config.ALPHA)

    # --- Visualization ---
    
    table = Table(title="Comparison: Stale vs. JIT Evaluation", box=box.HEAVY_EDGE)
    table.add_column("Architecture", style="bold white")
    table.add_column("Effective Trust", justify="right")
    table.add_column("Required Threshold", justify="right")
    table.add_column("Decision", justify="center")
    table.add_column("Security Verdict", justify="center")

    # Row for V1
    verdict_v1 = "[red]VULNERABLE[/red]" if result_v1.decision else "SAFE"
    decision_v1 = "[red]PERMIT[/red]" if result_v1.decision else "[green]DENY[/green]"
    table.add_row(
        "V1 (Legacy/Stale)", 
        f"{trust_v1:.4f} (No Change)", 
        f"{result_v1.threshold:.4f}",
        decision_v1,
        verdict_v1
    )

    # Row for V2
    verdict_v2 = "[green]SECURE[/green]" if not result_v2.decision else "[red]UNSAFE[/red]"
    decision_v2 = "[green]DENY[/green]" if not result_v2.decision else "[red]PERMIT[/red]"
    table.add_row(
        "V2 (D-ABAC-Z JIT)", 
        f"{trust_v2:.4f} (Decayed)", 
        f"{result_v2.threshold:.4f}",
        decision_v2,
        verdict_v2
    )

    console.print(table)
    
    # --- Analysis Output ---
    console.print("\n[bold underline]Analysis:[/bold underline]")
    console.print(f"1. The environment risk spiked to [bold]{risk_high}[/bold], raising the bar to [bold]{result_v1.threshold:.2f}[/bold].")
    console.print("2. In [bold]V1[/bold], the system used the old trust score (0.90), ignoring the 30-unit inactivity gap.")
    console.print("   -> Result: Attacker re-uses an idle session to access high-risk data.")
    console.print(f"3. In [bold]V2[/bold], the system calculated decay on-the-fly: 0.9 * e^(-0.05*30) = {trust_v2:.2f}.")
    console.print(f"   -> Result: {trust_v2:.2f} < {result_v2.threshold:.2f}. Access blocked.")
    
    console.print("\n[italic]This confirms the Alloy Trace findings in Appendix D.3.[/italic]")

if __name__ == "__main__":
    run()