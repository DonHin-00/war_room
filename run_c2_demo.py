#!/usr/bin/env python3
import time
import threading
from rich.console import Console
from rich.panel import Panel
from ant_swarm.c2.server import OvermindServer
from ant_swarm.c2.drone import Drone

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v17: C2 BOTNET ARCHITECTURE[/]", expand=False))

    # 1. Start Overmind
    c2 = OvermindServer(port=8080)
    c2.start()

    # Give it a sec to bind
    time.sleep(1)

    # 2. Deploy Drone
    drone = Drone(c2_url="http://localhost:8080")
    # Run drone in thread to simulate independent process
    drone_thread = threading.Thread(target=drone.deploy)
    drone_thread.start()

    # 3. Monitor (Main thread acts as Operator View)
    console.print("\n[OPERATOR] 📺 Monitoring C2 Traffic...")
    drone_thread.join()

    console.print("\n[OPERATOR] 🛑 Mission Complete. Shutting down C2.")
    c2.stop()

if __name__ == "__main__":
    main()
