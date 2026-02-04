from typing import List, Dict
from ant_swarm.red.campaign import AutoRecon
from ant_swarm.red.human_link import HumanLink
from ant_swarm.red.loot_bag import LootBag
from rich.console import Console

console = Console()

class Strategist:
    """
    The Red Team Campaign Manager.
    Aggregates AutoRecon data and triggers HumanLink for Major targets.
    INTEGRATED: Uses LootBag for Exfil/Infil.
    """
    def __init__(self, recon: AutoRecon):
        self.recon = recon
        self.loot_bag = LootBag()

    def execute_campaign(self):
        # 1. Mass Scale Auto Recon
        self.recon.scan_mass_scale()
        criticals = self.recon.get_critical_intel()
        noise = self.recon.get_noise_report()

        # EXFIL: Send noise (secrets) to Loot Bag
        for finding in noise:
            self.loot_bag.queue_for_exfil(f"SECRET found in {finding['file']}")

        # Flush leftovers
        self.loot_bag.trigger_exfil()

        console.print(f"\n[STRATEGIST] 🗺️ Strategic Map Updated. {len(noise)} secrets exfiltrated.")

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
        console.print(f"[STRATEGIST] 🚀 WEAPON DEPLOYED against {intel['file']}.")

        # INFIL: Smuggle the payload in
        # Simulated fragmentation of a payload script
        import base64
        payload_script = "print('Pwned')"
        b64 = base64.b64encode(payload_script.encode()).decode()
        # Split into chunks
        fragments = [b64[:4], b64[4:]]

        weapon = self.loot_bag.smuggle_weapon_in(fragments)
        console.print(f"[STRATEGIST] Weapon Reassembled: {weapon}")
