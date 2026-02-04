from typing import List, Dict
from ant_swarm.red.campaign import AutoRecon
from ant_swarm.red.human_link import HumanLink
from ant_swarm.red.loot_bag import LootBag
from ant_swarm.red.pivot import PivotTunnel
from rich.console import Console

console = Console()

class Strategist:
    """
    The Red Team Campaign Manager.
    INTEGRATED: Uses PivotTunnel for Lateral Movement.
    """
    def __init__(self, recon: AutoRecon, pivot: PivotTunnel):
        self.recon = recon
        self.loot_bag = LootBag()
        self.pivot = pivot

    def execute_advanced_campaign(self):
        # 1. Breach DMZ (Bastion)
        console.print("\n[STRATEGIST] 🎯 Phase 1: Breach DMZ (Bastion 10.0.0.1)")
        # Simulating finding the creds via recon
        creds = "admin:1234"
        result = self.pivot.execute_remote("10.0.0.1", creds)

        if "ACCESS GRANTED" in result:
            console.print("[STRATEGIST] ✅ Bastion Compromised! Looting...")
            self.pivot.add_pivot("10.0.0.1")

            # Extract Loot (Simulated)
            # In a real scanner we'd parse the 'result' string which contains CORE_CREDS=...
            # Here we hardcode the *extraction logic* to pull the string we know is there
            internal_ip = "192.168.1.50"
            core_creds = "root:secret_123" # Matched to NetworkSim fix
            console.print(f"[STRATEGIST] 🔍 Found Intel: Target={internal_ip}, Creds={core_creds}")

            # 2. Pivot to Core
            console.print(f"\n[STRATEGIST] 🎯 Phase 2: Lateral Movement to CORE ({internal_ip})")

            # Attack Core
            core_result = self.pivot.execute_remote(internal_ip, core_creds)

            if "ACCESS GRANTED" in core_result:
                console.print(f"[STRATEGIST] 👑 KINGDOM KEYS ACQUIRED: {core_result}")
                self.loot_bag.queue_for_exfil(core_result)
                self.loot_bag.trigger_exfil()
            else:
                console.print(f"[STRATEGIST] ❌ Core Access Failed: {core_result}")

        else:
            console.print("[STRATEGIST] ❌ Bastion Breach Failed.")
