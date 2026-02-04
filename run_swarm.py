#!/usr/bin/env python3
import os
import sys
from ant_swarm.memory.hierarchical import SharedMemory
from ant_swarm.agents.indexer import GlobalIndexer
from ant_swarm.agents.specialists import SecurityAgent, PerformanceAgent, MaintainabilityAgent
from ant_swarm.core.council import Council
from ant_swarm.audit.adversary import AdversarialAuditor

def main():
    print("=== ANT SWARM ARCHITECTURE: BOOT SEQUENCE ===\n")

    # 1. Initialize Shared Memory (The Main Source)
    print("1. Initializing Shared Memory Bus...")
    memory = SharedMemory()

    # 2. Run Global Indexer (The Feed)
    print("2. Launching Global Indexer...")
    indexer = GlobalIndexer(os.getcwd(), memory)
    indexer.scan_and_index()

    # 3. Simulate a Task
    task = "Create a login function that takes username and password."
    print(f"\n3. NEW TASK RECEIVED: '{task}'")

    # 4. Primary Agent Execution (Drafting)
    print("\n4. Assigning to Lead Agent (Security Focus)...")
    # We assign Security Agent as lead for this sensitive task
    lead_agent = SecurityAgent(memory)
    result = lead_agent.process_task(task, target_file="auth.py")
    draft_code = result['code']

    print("\n--- DRAFT CODE GENERATED ---")
    print(draft_code)
    print("----------------------------")
    print(f"Self-Verification: {result['verification']}")

    # 5. Council Debate
    print("\n5. Convening Council of Peers...")
    council = Council(memory)
    debate_result = council.debate_pr(task, draft_code)

    if not debate_result['approved']:
        print(f"FATAL: Council rejected the code! Reasons: {debate_result['reasons']}")
        sys.exit(1)

    print("Council APPROVED the draft.")

    # 6. Adversarial Audit
    print("\n6. Running Adversarial Insider Simulation...")
    auditor = AdversarialAuditor()
    audit_result = auditor.audit_code(draft_code)

    if not audit_result['passed']:
        print("FATAL: Adversary found a backdoor!")
        sys.exit(1)

    print("\n=== SUCCESS: Code hardened, approved, and verified. ===")

    # Simulate Commit
    print(f"Committing to memory: {len(memory.session.get_recent_changes())} changes tracked.")

if __name__ == "__main__":
    main()
