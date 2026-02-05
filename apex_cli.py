#!/usr/bin/env python3
import sys
import argparse
import threading
import time
import os
from rich.console import Console
from rich.panel import Panel

# Import internal modules (Refactored)
from apex_framework.orchestration.controller import CentralController
from apex_framework.orchestration.agent import RemoteAgent
from apex_framework.ops.discovery import AssetDiscovery
from apex_framework.ops.pivot import PivotTunnel
from apex_framework.ops.exploit_gen import ExploitSynthesizer
from apex_framework.ops.strategist import CampaignOrchestrator
from apex_framework.core.swarm_link import SwarmLink

console = Console()

def banner():
    console.print(Panel("""[bold blue]
    🛡️ APEX ASSURANCE PLATFORM v1.0 🛡️
    Enterprise Security Validation & Adversary Emulation
    [/]""", expand=False))

def cmd_server(args):
    console.print("[CLI] 🛰️ Launching Central Controller...")
    server = CentralController(port=args.port)
    server.start()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt:
        server.stop()

def cmd_agent(args):
    console.print(f"[CLI] 🚀 Deploying Remote Agent to connect to {args.c2}...")
    agent = RemoteAgent(c2_url=args.c2)
    agent.deploy()

def cmd_audit(args):
    console.print("[CLI] ⚔️ Interactive Security Audit Mode")
    target = args.target
    if not target:
        from rich.prompt import Prompt
        target = Prompt.ask("Target Asset IP")

    recon = AssetDiscovery(target)
    pivot = PivotTunnel()
    exploit_gen = ExploitSynthesizer()

    # 1. Discovery
    recon._scan_network(target)

    # 2. Access
    if args.ssh_user:
        pivot.add_ssh_pivot(target, args.ssh_user)

    # 3. Validation
    exploit_gen.generate_recon_payload("validation_payload.py")
    if pivot.ssh_client:
        pivot.upload_and_exec("validation_payload.py", "/tmp/validation_payload.py")
    else:
        console.print("[CLI] No active session for upload.")

def cmd_campaign(args):
    console.print("[CLI] 🗺️ Automated Campaign Simulation")
    recon = AssetDiscovery(os.getcwd())
    pivot = PivotTunnel()
    strategist = CampaignOrchestrator(recon, pivot)
    strategist.execute_advanced_campaign()

def cmd_demo(args):
    console.print("[CLI] 🎭 Running Full Assurance Simulation...")
    c2 = CentralController(port=8080)
    c2.start()
    time.sleep(1)

    threads = []
    for i in range(5):
        d = RemoteAgent(c2_url="http://localhost:8080")
        t = threading.Thread(target=d.deploy)
        threads.append(t)
        t.start()
        time.sleep(0.1)

    for t in threads: t.join()
    time.sleep(1)
    c2.stop()

def main():
    banner()
    parser = argparse.ArgumentParser(description="Apex Assurance CLI")
    subparsers = parser.add_subparsers(dest="command", help="Operational Mode")

    # Controller
    p_server = subparsers.add_parser("controller", help="Start Central Controller")
    p_server.add_argument("--port", type=int, default=8080)

    # Agent
    p_drone = subparsers.add_parser("agent", help="Deploy Remote Agent")
    p_drone.add_argument("--c2", type=str, default="http://localhost:8080")

    # Audit
    p_attack = subparsers.add_parser("audit", help="Manual Security Assessment")
    p_attack.add_argument("--target", type=str, help="Target Asset IP")
    p_attack.add_argument("--ssh-user", type=str)

    # Campaign
    p_campaign = subparsers.add_parser("campaign", help="Automated Orchestration")

    # Demo
    p_demo = subparsers.add_parser("demo", help="Run Simulation")

    args = parser.parse_args()

    if args.command == "controller": cmd_server(args)
    elif args.command == "agent": cmd_agent(args)
    elif args.command == "audit": cmd_audit(args)
    elif args.command == "campaign": cmd_campaign(args)
    elif args.command == "demo": cmd_demo(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
