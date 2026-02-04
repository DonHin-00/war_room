from typing import List, Dict
from ant_swarm.red.campaign import AutoRecon
from ant_swarm.red.human_link import HumanLink
from rich.console import Console

console = Console()

class Strategist:
    """
    The Red Team Campaign Manager.
    Aggregates AutoRecon data and triggers HumanLink for Major targets.
    """
    def __init__(self, recon: AutoRecon):
        self.recon = recon

    def execute_campaign(self):
        # 1. Mass Scale Auto Recon
        self.recon.scan_mass_scale()
        criticals = self.recon.get_critical_intel()
        noise = self.recon.get_noise_report()

        console.print(f"\n[STRATEGIST] 🗺️ Strategic Map Updated. {len(noise)} Low-Priority targets suppressed.")

        # 2. Strategic Assessment
        if not criticals:
            console.print("[STRATEGIST] No Major Targets found. Campaign entering Dormant Mode.")
            return

        console.print(f"[STRATEGIST] {len(criticals)} MAJOR TARGETS identified. Elevating to Human Command.")

        # 3. Human Loop for Major Targets
        for intel in criticals:
            authorized = HumanLink.request_intervention(intel)

            if authorized:
                self._deploy_weapon(intel)
            else:
                console.print("[STRATEGIST] Standing down. Target logged for future review.")

    def _deploy_weapon(self, intel: Dict):
        console.print(f"[STRATEGIST] 🚀 WEAPON DEPLOYED against {intel['file']}. Exploit Generated.")
        # In a full simulation, this would call 'Breaker' to generate the payload
