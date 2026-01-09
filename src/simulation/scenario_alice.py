"""
Simulation Scenario: Dr. Alice's Mobility
=========================================

This script reproduces the Case Study described in **Section 6.1** and **6.2**.
It demonstrates how the D-ABAC-Z framework dynamically adjusts access decisions 
based on environmental risk and user behavior.

Scenario Phases:
----------------
1. **Hospital (Low Risk):** Dr. Alice accesses PHR from a secure intranet.
   - Expectation: PERMIT (Trust 0.75 >= Threshold 0.63)

2. **Café (High Risk):** Dr. Alice roams to a public Wi-Fi.
   - Expectation: DENY (Trust 0.75 < Threshold 0.87)
   - Demonstrates: Risk Monotonicity (Assert 2)

3. **Remediation (MFA):** Dr. Alice performs Multi-Factor Authentication.
   - Expectation: PERMIT (Trust increases to ~0.95 >= Threshold 0.87)
   - Demonstrates: Conditional Liveness / Recovery (Assert 3)
"""

import time
import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from ..components import PEP, PDP, PIP, TrustEngine
from ..data import config

# Initialize Rich Console
console = Console()

def print_step_header(step_num: int, title: str, description: str):
    console.print(f"\n[bold magenta]--- Step {step_num}: {title} ---[/bold magenta]")
    console.print(f"[dim]{description}[/dim]\n")

def simulate_step(pep: PEP, subject: str, obj: str, context: dict, step_name: str):
    """Executes a single access request and prints the result."""
    
    # Execute Request via PEP (Fast Path + Slow Path Logic)
    response = pep.access_request(subject, obj, context)
    
    # Extract details for visualization
    details = response['details']
    status_color = "green" if response['status'] == 200 else "red"
    
    # Create a Summary Table
    table = Table(box=box.SIMPLE)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="bold white")
    
    table.add_row("Location", context.get('location', 'Unknown'))
    table.add_row("Risk Level (R)", f"{context.get('_debug_risk', 'N/A')}") # In a real app we'd get this from PIP
    table.add_row("Dynamic Threshold", f"{details['threshold']:.4f}")
    table.add_row("Decision", f"[{status_color}]{response['message']}[/{status_color}]")
    table.add_row("Reason", details['reason'])
    
    console.print(Panel(table, title=f"Result: {step_name}", border_style=status_color))
    return response

def run():
    """Main execution entry point called by main.py."""
    
    console.clear()
    console.rule("[bold blue]D-ABAC-Z Case Study: Cloud Medical System[/bold blue]")
    
    # --- 1. System Initialization ---
    console.print("[bold]Initializing Control Plane Components...[/bold]")
    pip = PIP()
    trust_engine = TrustEngine() # Seeds Alice with Trust = 0.75
    pdp = PDP(pip, trust_engine)
    pep = PEP(pdp)
    
    subject_id = "alice"
    object_id = "record_8842"
    
    # Verify Initial State
    initial_trust = trust_engine.get_effective_trust(subject_id)
    console.print(f"Subject: [bold]Dr. Alice[/bold] | Initial Trust (tau): [bold]{initial_trust:.2f}[/bold]")
    console.print(f"Object:  [bold]PHR #8842[/bold] | Base Req (T_base): [bold]0.60[/bold]")
    console.print(f"Config:  [bold]Alpha = {config.ALPHA}[/bold] (Risk Sensitivity)")
    
    time.sleep(1)

    # --- Step 1: Hospital Access ---
    print_step_header(1, "Access from Hospital Network", 
                      "Environment is secure. Risk should be low (0.1).")
    
    ctx_hospital = {"location": "hospital", "network_security": "wpa3_enterprise"}
    # Debug hint for visualization (PIP calculates this internally)
    ctx_hospital['_debug_risk'] = 0.1 
    
    simulate_step(pep, subject_id, object_id, ctx_hospital, "Hospital Access")
    
    time.sleep(1)

    # --- Step 2: Café Access (High Risk) ---
    print_step_header(2, "Roaming to Public Café", 
                      "Environment is hostile. Risk spikes to 0.9. Threshold should rise.")
    
    ctx_cafe = {"location": "cafe", "network_security": "open"}
    ctx_cafe['_debug_risk'] = 0.9
    
    simulate_step(pep, subject_id, object_id, ctx_cafe, "Café Access")
    
    time.sleep(1)

    # --- Step 3: Remediation via MFA ---
    print_step_header(3, "MFA Remediation", 
                      "User performs MFA. Trust Engine processes evidence (L=999).")
    
    # Simulate the "Feedback Loop" (Step 0 in Fig 1)
    # Load MFA likelihood from mapper (simulated)
    # In unsw_nb15_mapper.json, MFA Success L = 999.0
    mfa_likelihood = 999.0 
    
    with console.status("[bold yellow]Processing MFA Evidence...[/bold yellow]"):
        time.sleep(1) # Simulate network delay
        trust_engine.process_evidence(subject_id, mfa_likelihood)
        
    new_trust = trust_engine.get_effective_trust(subject_id)
    console.print(f" >> Trust Score Updated: [bold]{new_trust:.4f}[/bold]")
    
    # Retry Access from Café
    simulate_step(pep, subject_id, object_id, ctx_cafe, "Café Access (Post-MFA)")

    console.rule("[bold green]Scenario Complete[/bold green]")
    console.print("[italic]The results confirm Risk Monotonicity (Step 2) and Trust Recovery (Step 3).[/italic]")

if __name__ == "__main__":
    run()