#!/usr/bin/env python3
import time
import threading
from rich.console import Console
from rich.panel import Panel
from ant_swarm.c2.server import OvermindServer
from ant_swarm.c2.drone import Drone

console = Console()

def main():
    console.print(Panel("[bold red]ANT SWARM v18: SWARM INTELLIGENCE (MAP REDUCE)[/]", expand=False))

    # 1. Start Overmind
    c2 = OvermindServer(port=8080)
    c2.start()
    time.sleep(1)

    # 2. Deploy 10 Drones (The Swarm)
    console.print(f"\n[OPERATOR] 🚀 Launching 10 Drones against Hardened Target...")
    threads = []
    for i in range(10):
        # Create unique instances
        d = Drone(c2_url="http://localhost:8080")
        t = threading.Thread(target=d.deploy)
        threads.append(t)
        t.start()
        time.sleep(0.1) # Stagger launch slightly

    # 3. Monitor
    console.print("\n[OPERATOR] 📺 Monitoring Swarm Convergence...")
    for t in threads:
        t.join()

    # Give C2 time to aggregate final results
    time.sleep(2)

    console.print("\n[OPERATOR] 🛑 Mission Complete. Shutting down C2.")
    c2.stop()

if __name__ == "__main__":
    main()
