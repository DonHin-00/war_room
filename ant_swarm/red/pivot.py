from rich.console import Console
from ant_swarm.red.network_sim import NetworkSim

console = Console()

class PivotTunnel:
    """
    Lateral Movement Module.
    Wraps commands to execute through a compromised host.
    """
    def __init__(self, network: NetworkSim):
        self.network = network
        self.pivots = [] # List of compromised hosts to route through

    def add_pivot(self, host_ip: str):
        console.print(f"[PIVOT] 🌉 Established Tunnel Node: {host_ip}")
        self.pivots.append(host_ip)

    def execute_remote(self, target_ip: str, payload: str) -> str:
        """
        Routes the attack through the last pivot.
        """
        if not self.pivots:
            # Direct connection from Internet
            source = "INTERNET" # Virtual IP
        else:
            source = self.pivots[-1]
            console.print(f"[PIVOT] 🔀 Routing: INTERNET -> {source} -> {target_ip}")

        return self.network.route_packet(source, target_ip, payload)
