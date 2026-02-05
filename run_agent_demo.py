#!/usr/bin/env python3
import sys
import time
import shutil
import os
from rich.console import Console
from rich.panel import Panel

console = Console()

def main():
    console.print(Panel("[bold cyan]APEX v20: AGENT DEMO (DISKLESS)[/]", expand=False))

    # 1. Start Logic Server
    from apex_framework.orchestration.logic_server import LogicServer
    brain = LogicServer(port=9090)
    brain.start()
    time.sleep(1)

    # 2. Activate DCL
    from apex_framework.orchestration import dynamic_loader
    dynamic_loader.install(c2_url="http://localhost:9090")

    # 3. Demonstrate Ephemeral Streaming
    console.print("\n[SCENARIO] 👻 Agent requesting 'Discovery' capabilities...")

    # Clean sys.modules to force stream
    for mod in ["apex_framework.ops.discovery", "apex_framework.ops.strategist", "apex_framework.ops.pivot"]:
        if mod in sys.modules: del sys.modules[mod]

    try:
        import apex_framework.ops.discovery
        console.print("[AGENT] ✅ Capability Acquired via Stream.")
        recon = apex_framework.ops.discovery.AssetDiscovery(".")
        recon.scan_mass_scale()
    except ImportError as e:
        console.print(f"[AGENT] ❌ Failed: {e}")

    console.print("\n[SCENARIO] 🛑 Stopping Controller.")
    brain.stop()

if __name__ == "__main__":
    main()
