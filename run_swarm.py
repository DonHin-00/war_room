#!/usr/bin/env python3
import os
import sys
from rich.console import Console
from rich.panel import Panel
from ant_swarm.red.campaign import AutoRecon
from ant_swarm.red.strategist import Strategist
from ant_swarm.red.network_sim import NetworkSim
from ant_swarm.red.pivot import PivotTunnel

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v14: SEGREGATED TARGET & PIVOTING[/]", expand=False))

    # 1. Initialize Network Simulation
    network = NetworkSim()

    # 2. Initialize Red Team with Pivot Capabilities
    recon = AutoRecon(os.getcwd())
    pivot = PivotTunnel(network)
    strategist = Strategist(recon, pivot)

    # 3. Prove Direct Access Fails (Firewall Test)
    console.print("\n[SCENARIO] 🛑 Verifying Segregation...")
    direct_result = network.route_packet("INTERNET", "192.168.1.50", "hello")
    if "REFUSED" in direct_result:
        console.print("[BLUE] 🛡️ Firewall holding. Direct access to Core is blocked.")
    else:
        console.print("[RED] ❌ ERROR: Firewall failed.")
        sys.exit(1)

    # 4. Execute Advanced Campaign (Pivot)
    strategist.execute_advanced_campaign()

if __name__ == "__main__":
    main()
