#!/usr/bin/env python3
import os
import sys
from rich.console import Console
from rich.panel import Panel
from ant_swarm.red.campaign import AutoRecon
from ant_swarm.red.strategist import Strategist

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v12: ENHANCED RED TEAM (LOOT BAG)[/]", expand=False))

    # 1. Setup Environment
    with open("target_vuln.py", "w") as f:
        f.write("import os\n# TODO: Fix this RCE\nos.system(input())")

    # Generate enough noise to trigger a burst exfil
    with open("target_noise_1.txt", "w") as f: f.write("API_KEY=A")
    with open("target_noise_2.txt", "w") as f: f.write("API_KEY=B")
    with open("target_noise_3.txt", "w") as f: f.write("API_KEY=C")

    # 2. Initialize
    recon = AutoRecon(os.getcwd())
    strategist = Strategist(recon)

    # 3. Execute Campaign
    try:
        strategist.execute_campaign()
    except KeyboardInterrupt:
        pass

    # Cleanup
    if os.path.exists("target_vuln.py"): os.remove("target_vuln.py")
    for i in range(1,4):
        if os.path.exists(f"target_noise_{i}.txt"): os.remove(f"target_noise_{i}.txt")

if __name__ == "__main__":
    main()
