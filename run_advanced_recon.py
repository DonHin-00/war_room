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
    console.print(Panel("[bold magenta]APEX v23: 2026 REAL RECON (LOTL + AI)[/]", expand=False))

    # 1. Setup Environment (Simulated 2026 Targets)
    # Mocking Observability files for file scanner
    with open("datadog.yaml", "w") as f: f.write("api_key: dd_fake_key")
    with open("package.json", "w") as f: f.write('{"dependencies": {"vulnerable-lib": "1.0.0"}}')

    # Mocking ProcFS entries for LOTL test (since we can't easily spin up docker/k8s here)
    # We will create fake /proc files in a local directory and patch the LOTL class to read them?
    # No, that's too much patching.
    # We will rely on reading the REAL /proc of the sandbox environment.
    # It likely has /proc/net/tcp.

    # 2. Start C2
    c2 = CentralController(port=8080)
    c2.start()

    # Inject a 2026 Recon Order
    # The agent handles RECON_2026 by calling AssetDiscovery.scan_mass_scale()
    c2.server.RequestHandlerClass.dispatcher.job_queue.put({"type": "RECON_2026", "id": "FUTURE_TASK"})

    time.sleep(1)

    # 3. Deploy Agent
    console.print("\n[SCENARIO] 🚀 Deploying Agent (Scanning Sandbox Environment)...")
    agent = RemoteAgent(c2_url="http://localhost:8080")
    t = threading.Thread(target=agent.deploy)
    t.start()

    # Monitor
    time.sleep(10)

    console.print("\n[SCENARIO] 🛑 Mission Complete.")
    c2.stop()

    # Cleanup
    if os.path.exists("datadog.yaml"): os.remove("datadog.yaml")
    if os.path.exists("package.json"): os.remove("package.json")

if __name__ == "__main__":
    main()
