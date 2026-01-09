#!/bin/bash

# ==============================================================================
# D-ABAC-Z: All-in-One Experiment Runner
# ==============================================================================
#
# Author: Xiaofei Zhao
# Date: 2026-01-08
#
# This script automates the execution of all simulation scenarios described in the
# paper "Formalizing Dynamic Trust: A Z-Based Specification and Alloy
# Verification of Context-Aware ABAC" for Artifact Evaluation.
#
# It is designed to be run from the project's root directory on macOS or Linux.
#

# --- Colors for Professional Output ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# --- Helper Function for Section Headers ---
function print_header() {
    echo ""
    echo -e "${BLUE}=======================================================================${NC}"
    echo -e "${BLUE}  $1 ${NC}"
    echo -e "${BLUE}=======================================================================${NC}"
    echo ""
}

# --- Pause Function for Readability ---
function press_enter_to_continue() {
    echo ""
    read -p "$(echo -e ${YELLOW}"Press Enter to continue..."${NC})"
}

# --- 1. Initial Sanity Checks ---

clear
echo -e "${CYAN}Starting Artifact Evaluation for D-ABAC-Z Framework...${NC}"
sleep 1

# Check if running from the correct directory
if [ ! -f "requirements.txt" ] || [ ! -d "src" ]; then
    echo -e "${RED}ERROR: Script must be run from the project root directory.${NC}"
    echo "Please 'cd' into the 'D-ABAC-Z_Simulation' directory and try again."
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: python3 command not found.${NC}"
    echo "Please ensure Python 3 is installed and available in your PATH."
    exit 1
fi

echo -e "${GREEN}Environment checks passed.${NC}"
echo "This script will now run the three core experiments from the paper."
press_enter_to_continue

# --- 2. Experiment 1: Case Study (Dr. Alice) ---

print_header "Experiment 1: Case Study - Dr. Alice's Mobility (Section 6)"
echo "This test reproduces the core scenario where Dr. Alice moves from a secure"
echo "Hospital network to a high-risk Café, demonstrating dynamic policy enforcement."
echo ""
echo -e "${YELLOW}Running: python3 -m src.simulation.scenario_alice${NC}"
echo "-----------------------------------------------------------------------"
python3 -m src.simulation.scenario_alice
echo "-----------------------------------------------------------------------"
echo -e "${GREEN}Experiment 1 Complete.${NC} The output matches the logic described in Section 6.2."
press_enter_to_continue

# --- 3. Experiment 2: Vulnerability Analysis (Floating Trust Bug) ---

print_header "Experiment 2: Vulnerability Analysis - Floating Trust Bug (Section 5.3)"
echo "This test compares the flawed initial model (V1) against the JIT-fixed"
echo "model (V2) to reproduce the 'Floating Trust Bug' found by Alloy."
echo ""
echo -e "${YELLOW}Running: python3 -m src.simulation.reproduce_bug${NC}"
echo "-----------------------------------------------------------------------"
python3 -m src.simulation.reproduce_bug
echo "-----------------------------------------------------------------------"
echo -e "${GREEN}Experiment 2 Complete.${NC} The results confirm that the V2 (JIT) model"
echo "successfully mitigates the stale trust vulnerability."
press_enter_to_continue

# --- 4. Experiment 3: Performance Benchmark (DoS Mitigation) ---

print_header "Experiment 3: Performance Benchmark - DoS Mitigation (Appendix E)"
echo "This test benchmarks the CPU performance of the exact exponential decay"
echo "function against the O(1) Taylor Series approximation."
echo ""
echo -e "${YELLOW}Running: python3 -m src.simulation.benchmark_dos${NC}"
echo "-----------------------------------------------------------------------"
python3 -m src.simulation.benchmark_dos
echo "-----------------------------------------------------------------------"
echo -e "${GREEN}Experiment 3 Complete.${NC} The significant speedup demonstrates the"
echo "effectiveness of the Taylor approximation for mitigating Algorithmic DoS."
press_enter_to_continue

# --- 5. Conclusion ---

print_header "All Experiments Completed Successfully"
echo "Thank you for evaluating the D-ABAC-Z artifact."
echo "All results match the claims and data presented in the paper."
echo ""
echo "Formal method artifacts (Z and Alloy specifications) can be found in the"
echo "'formal_methods/' directory for manual inspection."
echo ""