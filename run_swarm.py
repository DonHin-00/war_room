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
    print("=== ANT SWARM v5: TRANSPARENT CAPABILITY ===\n")

    hive = HiveMind()
    ooda = OODALoop(hive)

    # 1. Simulate Detection of "Amateur" Code
    print("[SCENARIO] User submits amateur code request: 'make a login func'")
    print("[HIVE] 🧠 Analysis: Request is vague. Complexity analysis suggests high risk of poor implementation.")

    # Trigger Professional Doctrine
    hive.memory.defcon = 3 # Elevated Risk due to vagueness
    print(f"[OODA] ⚙️ Doctrine Selected: Active Defense (Proactive Engineering)")

    # 2. MicroLM Generation with Transparency
    print("\n[ACT] MicroLM Engineering Solution...")
    lm = MicroLM()
    context = {}
    doctrine = ooda.execute_cycle("login")

    # We purposefully inject a "need" for repair to show off
    options = lm.generate_with_doctrine("login", doctrine, context, k=3)

    # 3. Council Review
    print("\n[COUNCIL] Reviewing Options with Deep Analysis...")
    council = Council(hive)
    decision = council.select_best_option("login", options)

    if decision['approved']:
        print(f"\n🎉 RESULT: {decision['selected_variant']} Profile Selected.")
        print("---------------------------------------------------")
        print("          TRANSFORMATION REPORT")
        print("---------------------------------------------------")
        print("INPUT:  'make a login func'")
        print("OUTPUT:")
        print(decision['code'])
        print("---------------------------------------------------")
        print(f"CAPABILITIES ADDED: {len(decision['improvements'])}")
        for imp in decision['improvements']:
            print(f"  + {imp}")
        print("---------------------------------------------------")
    else:
        print("❌ Failure.")

if __name__ == "__main__":
    main()
