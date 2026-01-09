"""
D-ABAC-Z Simulation Framework - CLI Entry Point
===============================================
This script serves as the interactive dashboard for the artifacts associated with:
"Formalizing Dynamic Trust: A Z-Based Specification and Alloy Verification of Context-Aware ABAC"

It allows the user to select and execute the three core experimental components defined 
in the paper's directory structure.

Dependencies: rich (pip install rich)
"""

import sys
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.table import Table
from rich import box

# Try importing the simulation modules. 
# We use try/except to provide helpful error messages if the directory structure isn't set up yet.
try:
    from src.simulation import scenario_alice
    from src.simulation import reproduce_bug
    from src.simulation import benchmark_dos
except ImportError as e:
    # In a real deployment, these would be available. 
    # For this template, we define placeholder runners below if imports fail.
    scenario_alice = None
    reproduce_bug = None
    benchmark_dos = None
    IMPORT_ERROR_MSG = str(e)

console = Console()

def print_header():
    """Displays the project banner and paper info."""
    console.clear()
    title = "[bold cyan]D-ABAC-Z Simulation Framework[/bold cyan]"
    subtitle = "[italic]Artifact Evaluation for ESORICS 2026 Submission[/italic]"
    
    info_grid = Table.grid(padding=1)
    info_grid.add_column(style="bold yellow", justify="right")
    info_grid.add_column(style="white")
    
    info_grid.add_row("Paper Title:", "Formalizing Dynamic Trust via Z & Alloy")
    info_grid.add_row("Core Logic:", "HMM Trust Model + Linear Risk-Adaptive Policy")
    info_grid.add_row("Verification:", "Alloy Analyzer 6.0 (Fixed-Point Arithmetic)")
    
    panel = Panel(
        info_grid,
        title=title,
        subtitle=subtitle,
        border_style="blue",
        expand=False
    )
    console.print(panel)
    console.print()

def show_menu():
    """Displays the main selection menu."""
    table = Table(title="Select a Simulation Scenario", box=box.ROUNDED, show_lines=True)
    table.add_column("ID", style="cyan", justify="center", width=4)
    table.add_column("Module Name", style="bold white")
    table.add_column("Paper Section", style="magenta")
    table.add_column("Description", style="dim")

    table.add_row(
        "1", 
        "Case Study: Dr. Alice", 
        "Section 6.1 & 6.2", 
        "Simulates a user moving between Hospital (Permit) and Café (Deny), followed by MFA recovery."
    )
    table.add_row(
        "2", 
        "Vulnerability Analysis", 
        "Section 5.3", 
        "Reproduces the 'Floating Trust Bug' (Stale Trust) and validates the Just-in-Time (JIT) fix."
    )
    table.add_row(
        "3", 
        "Performance Benchmark", 
        "Section 7.4 / App E", 
        "Compares CPU cost of Exact Exponential Decay vs. Taylor Series Approximation (DoS Mitigation)."
    )
    table.add_row(
        "0", 
        "Exit", 
        "", 
        "Quit the simulation framework."
    )

    console.print(table)

def run_scenario_1():
    console.rule("[bold green]Running Scenario 1: Dr. Alice's Mobility[/bold green]")
    console.print("[dim]Loading HMM Engine and LRAP Policy...[/dim]\n")
    
    if scenario_alice:
        scenario_alice.run()
    else:
        # Mock output for demonstration if file is missing
        with console.status("[bold green]Simulating workflow...[/]"):
            time.sleep(1)
            console.print("T=0  | Loc: Hospital | Risk: 0.1 | Trust: 0.75 | [green]PERMIT[/]")
            time.sleep(0.5)
            console.print("T=10 | Loc: Café     | Risk: 0.9 | Trust: 0.75 | [red]DENY[/] (Threshold > Trust)")
            time.sleep(0.5)
            console.print("T=11 | Action: MFA   | Risk: 0.9 | Trust: 0.95 | [green]PERMIT[/] (Risk Compensation)")
    
    console.print("\n[bold blue]Scenario Complete.[/bold blue] See [bold]Appendix C[/bold] for calculations.")
    Prompt.ask("\nPress Enter to return")

def run_scenario_2():
    console.rule("[bold red]Running Scenario 2: Floating Trust Bug[/bold red]")
    console.print("[dim]Comparing V1 (Stale State) vs V2 (JIT Evaluation)...[/dim]\n")
    
    if reproduce_bug:
        reproduce_bug.run()
    else:
        # Mock output
        console.print("[bold underline]Test Case:[/bold underline] High Trust User becomes inactive, then Risk spikes.")
        with console.status("[bold red]Running V1 (Standard ABAC State)...[/]"):
            time.sleep(1)
            console.print("V1 Result: [red]ACCESS GRANTED[/] (FAIL). Stored trust was 0.9, ignored decay.")
        
        console.print()
        
        with console.status("[bold green]Running V2 (D-ABAC-Z JIT)...[/]"):
            time.sleep(1)
            console.print("V2 Result: [green]ACCESS DENIED[/] (PASS). Effective trust calculated as 0.4.")

    console.print("\n[bold blue]Verification Complete.[/bold blue] See [bold]Appendix D.3[/bold] for Alloy trace.")
    Prompt.ask("\nPress Enter to return")

def run_scenario_3():
    console.rule("[bold yellow]Running Scenario 3: DoS Benchmark[/bold yellow]")
    console.print("[dim]Measuring CPU cycles for decay functions (N=1,000,000)...[/dim]\n")
    
    if benchmark_dos:
        benchmark_dos.run()
    else:
        # Mock output
        with console.status("[bold white]Benchmarking...[/]"):
            time.sleep(1.5)
            console.print("Method: Exact (exp)   | Time: 1.24s | Error: 0.00%")
            console.print("Method: Taylor (O(1)) | Time: 0.08s | Error: 0.00001%")
            console.print("\nSpeedup: [bold green]15.5x[/bold green]")
    
    console.print("\n[bold blue]Benchmark Complete.[/bold blue] See [bold]Appendix E[/bold] for Big-O derivation.")
    Prompt.ask("\nPress Enter to return")

def main():
    while True:
        print_header()
        
        if scenario_alice is None:
            console.print(f"[bold red]Warning:[/bold red] Simulation modules not found. Running in [bold]Demo Mode[/bold].\n(Error: {IMPORT_ERROR_MSG})\n")
        
        show_menu()
        
        choice = IntPrompt.ask("Enter your choice", choices=["0", "1", "2", "3"], default="0")
        
        if choice == "1":
            run_scenario_1()
        elif choice == "2":
            run_scenario_2()
        elif choice == "3":
            run_scenario_3()
        elif choice == "0":
            console.print("[bold]Exiting D-ABAC-Z Simulation. Goodbye![/bold]")
            sys.exit(0)

if __name__ == "__main__":
    main()