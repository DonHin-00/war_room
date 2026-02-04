#!/usr/bin/env python3
import os
import sys
from ant_swarm.core.hive import HiveMind
from ant_swarm.core.ooda import OODALoop
from ant_swarm.core.micro_lm import MicroLM
from ant_swarm.core.council import Council
from ant_swarm.agents.indexer import GlobalIndexer
from ant_swarm.agents.reverse_engineer import ReverseEngineerAgent
from ant_swarm.support.external_storage import LongTermDrive
from ant_swarm.support.coprocessor import Coprocessor
from ant_swarm.support.gatekeeper import SecureGateway

def main():
    print("=== ANT SWARM v8: EXTERNAL MODULES & GATEKEEPER ===\n")

    hive = HiveMind()

    # Initialize Support Modules
    storage = LongTermDrive()
    coprocessor = Coprocessor(workers=4)
    gatekeeper = SecureGateway()

    # Attach "Hanging Off" Modules
    hive.attach_support(storage, coprocessor, gatekeeper)

    ooda = OODALoop(hive)

    # 1. Demonstrate Gatekeeper (Attack)
    print("\n[SCENARIO] 🛡️ External Interface: Processing Ingress...")
    attack_payload = "' OR 1=1; DROP TABLE users; --"
    result = gatekeeper.process_ingress("192.168.1.666", attack_payload)
    if result["status"] == "REJECTED":
        print("  - Attack Successfully Blocked.")

    # 2. Demonstrate Gatekeeper (Valid)
    print("\n[SCENARIO] 🛡️ External Interface: Valid Request...")
    valid_payload = "Create a login function."
    result = gatekeeper.process_ingress("10.0.0.5", valid_payload)
    if result["status"] != "ACCEPTED":
        print("  - Error: Valid request blocked.")
        sys.exit(1)

    task = result["payload"]

    # 3. MicroLM Generation
    print(f"\n[ACT] MicroLM Processing Task: '{task}'")
    lm = MicroLM()
    doctrine = ooda.execute_cycle(task)
    options = lm.generate_evolved_options(task, doctrine, {}, generations=1)

    # 4. Demonstrate Coprocessor Offloading (War Games)
    print("\n[COPROCESSOR] 🧠 Offloading Heavy War Games Simulation...")
    # We manually simulate the Council using the Coprocessor here for demo
    # In production, Council would hold a ref to Hive.coprocessor

    for opt in options:
        # Use the Coprocessor to run the parallel simulation
        survival = coprocessor.run_parallel_wargames(opt['code'], iterations=100)
        print(f"  > Variant '{opt['variant_name']}' Survival: {survival:.1%}")

    # 5. External Storage Persistence
    print("\n[STORAGE] 💾 Persisting results to LongTermDrive...")
    # Simulate a win
    hive.record_success(task, options[0], {})

if __name__ == "__main__":
    main()
