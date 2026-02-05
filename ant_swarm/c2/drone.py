import time
import requests
import json
import random
from ant_swarm.red.ghost import GhostProtocol
from rich.console import Console

console = Console()

class Drone:
    """
    Remote Agent.
    Connects to Overmind and executes MAPREDUCE orders.
    """
    def __init__(self, c2_url="http://localhost:8080"):
        self.id = f"DRONE_{random.randint(1000,9999)}"
        self.c2_url = c2_url
        self.active = True

    def deploy(self):
        # 1. Cloak (Simulated per previous requirement)
        GhostProtocol.cloak_process()

        # 2. Main Loop
        # console.print(f"[{self.id}] 🚀 Drone Active.")

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
                        # One shot for this demo to prevent infinite loops
                        self.active = False

                time.sleep(0.5)
            except Exception as e:
                console.print(f"[{self.id}] ⚠️ C2 Lost: {e}")
                break

    def _execute_orders(self, orders):
        # console.print(f"[{self.id}] ⚙️ Scanning Range: {orders['port_range']}")

        # Simulate Scanning the Hardened Target
        # In a real run, we'd use AutoRecon logic
        start, end = map(int, orders['port_range'].split('-'))
        findings = []

        # Simulated Hit: Port 22 and 80 are open
        for p in range(start, end):
            if p == 22 or p == 80:
                findings.append(f"OPEN:{p}")

        result = ", ".join(findings) if findings else "CLEAN"

        requests.post(f"{self.c2_url}/loot", json={"id": self.id, "content": result})
