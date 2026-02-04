#!/usr/bin/env python3
import os
import sys
from rich.console import Console
from rich.panel import Panel
from ant_swarm.red.campaign import AutoRecon
from ant_swarm.red.strategist import Strategist

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v11: RED TEAM CAMPAIGN TOOL[/]", expand=False))

    # 1. Setup Environment (Simulated Target)
    with open("target_vuln.py", "w") as f:
        f.write("import os\n# TODO: Fix this RCE\nos.system(input())")

    with open("target_noise.txt", "w") as f:
        f.write("API_KEY=12345")

    # 2. Initialize Red Team Modules
    recon = AutoRecon(os.getcwd())
    strategist = Strategist(recon)

    # 3. Execute Campaign
    # This will trigger the interactive Human Link
    try:
        strategist.execute_campaign()
    except KeyboardInterrupt:
        pass

    # Cleanup
    if os.path.exists("target_vuln.py"): os.remove("target_vuln.py")
    if os.path.exists("target_noise.txt"): os.remove("target_noise.txt")

if __name__ == "__main__":
    main()
