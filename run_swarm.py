#!/usr/bin/env python3
import os
import sys
from ant_swarm.core.hive import HiveMind
from ant_swarm.core.micro_lm import MicroLM
from ant_swarm.core.council import Council
from ant_swarm.agents.indexer import GlobalIndexer
from ant_swarm.agents.reverse_engineer import ReverseEngineerAgent

def main():
    print("=== ANT SWARM v3: INTEGRATED TOOLS ACTIVATION ===\n")

    # 1. Initialize Hive
    hive = HiveMind()
    indexer = GlobalIndexer(os.getcwd(), hive.memory)
    rev_eng = ReverseEngineerAgent(hive)

    # 2. Simulate Reverse Engineering (Live File)
    # We will use 'run_swarm.py' (this file) as the target since it exists!
    target_file = "run_swarm.py"
    print(f"\n[SCENARIO] User asks to analyze '{target_file}'.")

    hive.broadcast("FILE_CHANGED", {"filepath": target_file}, "User")

    # 3. MicroLM Generation with Tool-Assisted Repair
    task = "Create a secure login function."
    print(f"\n[SCENARIO] Generating Solutions with Self-Repair Loop...")

    lm = MicroLM()
    # Mocking a context
    context = {}

    options = lm.generate_top_k(task, "Security", context, k=3)

    for i, opt in enumerate(options):
        print(f"\nOption {i+1} ({opt['variant_name']}):")
        print(f"  Code Snippet: {opt['code'].splitlines()[0]}")
        print(f"  Tool Report: Syntax={opt['tool_report']['syntax']['valid']}, Security={opt['tool_report']['security']['safe']}")

    # 4. Council Selection
    print("\n[SCENARIO] Council Selecting Best Option...")
    council = Council(hive)
    decision = council.select_best_option(task, options)

    if decision['approved']:
        print(f"🎉 WINNER: {decision['selected_variant']}")
        print(f"Code:\n{decision['code']}")
    else:
        print("❌ All options rejected.")

if __name__ == "__main__":
    main()
