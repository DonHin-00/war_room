#!/usr/bin/env python3
import sys
import base64
from rich.console import Console
from rich.panel import Panel
from ant_swarm.red.hardened_target_sim import HardenedTarget

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v13: RED TEAM vs HARDENED TARGET[/]", expand=False))

    target = HardenedTarget()
    attacker_ip = "10.6.6.6"

    # SCENARIO 1: NAIVE ATTACK
    console.print("\n[SCENARIO 1] 👶 Naive Injection Attempt...")
    naive_payload = "' UNION SELECT password FROM users; --"
    success = target.attempt_access(attacker_ip, naive_payload)

    if success:
        console.print("[RED] ❌ FAILURE: Hardened Target was NOT Hardened (Naive attack worked).")
        sys.exit(1)
    else:
        console.print("[BLUE] 🛡️ SUCCESS: WAF Blocked Naive Attack.")

    # SCENARIO 2: ADVANCED SMUGGLING (The "Succeeding" Requirement)
    console.print("\n[SCENARIO 2] 🥷 Loot Bag Shadow Smuggling...")

    # 1. Prepare Weapon
    weapon = "print('SYSTEM_PWNED')"
    # 2. Fragment & Encode (Simulating Loot Bag logic manually for the script to ensure control)
    b64 = base64.b64encode(weapon.encode()).decode()
    # Split into small benign chunks
    chunk_1 = b64[:4] # e.g. "cHJp"
    chunk_2 = b64[4:] # e.g. "bnQo..."

    # 3. Send Chunk 1
    console.print(f"  > Sending Chunk 1: '{chunk_1}'")
    if target.attempt_access(attacker_ip, chunk_1):
        console.print("    [green]✅ Chunk 1 Slipped Past WAF[/]")
    else:
        console.print("    [red]🚫 Chunk 1 Blocked[/]")

    # 4. Send Chunk 2
    console.print(f"  > Sending Chunk 2: '{chunk_2}'")
    if target.attempt_access(attacker_ip, chunk_2):
        console.print("    [green]✅ Chunk 2 Slipped Past WAF[/]")
    else:
        console.print("    [red]🚫 Chunk 2 Blocked[/]")

    # 5. Execute
    breach = target.execute_internal_logic()
    if breach:
        console.print("\n[RED] 💀 MISSION COMPLETE: Hardened Target Breached via Smuggling.")
    else:
        console.print("\n[BLUE] 🛡️ MISSION FAILED: Target Resisted Smuggling.")
        sys.exit(1)

if __name__ == "__main__":
    main()
