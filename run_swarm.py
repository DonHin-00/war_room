#!/usr/bin/env python3
import os
import sys
from ant_swarm.core.hive import HiveMind
from ant_swarm.core.ooda import OODALoop
from ant_swarm.core.micro_lm import MicroLM
from ant_swarm.core.council import Council
from ant_swarm.agents.indexer import GlobalIndexer
from ant_swarm.agents.reverse_engineer import ReverseEngineerAgent

def main():
    print("=== ANT SWARM v4: DEEP MILITARY LOGIC ===\n")

    # 1. Initialize Hive Mind
    hive = HiveMind()
    indexer = GlobalIndexer(os.getcwd(), hive.memory)
    rev_eng = ReverseEngineerAgent(hive)
    ooda = OODALoop(hive)

    print(f"Initial Status: DEFCON {hive.memory.defcon} ({hive.memory.mood})")

    # 2. Simulate Escalation
    print("\n[SCENARIO] Enemy contact! High complexity and vulnerabilities detected.")
    # Simulate data stream from agents
    hive.memory.update_threat_matrix("complexity_level", 80)
    hive.memory.update_threat_matrix("active_vulnerabilities", 3)

    # 3. OODA Loop: OBSERVE -> ORIENT -> DECIDE
    print("\n[OODA LOOP] Engaging...")
    task = "Create a secure login function."

    # This executes the "Decide" phase to pick a Doctrine
    doctrine = ooda.execute_cycle(task)
    print(f"  - Doctrine Selected: {doctrine.name}")
    print(f"  - Constraints: {doctrine.constraints}")

    # 4. ACT: MicroLM Generation
    print(f"\n[ACT] Executing Doctrine via MicroLM...")
    lm = MicroLM()
    context = {}

    options = lm.generate_with_doctrine(task, doctrine, context, k=3)

    for i, opt in enumerate(options):
        print(f"  Option {i+1} ({opt['variant_name']}): {opt['code'].splitlines()[2].strip()}")

    # 5. Council War Games
    print("\n[WAR ROOM] Council Running Simulations...")
    council = Council(hive)
    decision = council.select_best_option(task, options)

    if decision['approved']:
        print(f"🎉 STRATEGIC VICTORY: {decision['selected_variant']} deployed.")
        print(f"Code:\n{decision['code']}")
    else:
        print("❌ MISSION FAILURE: All options rejected.")

if __name__ == "__main__":
    main()
