import random
import time
from rich.console import Console
from ant_swarm.red.network_sim import NetworkSim

console = Console()

class TrafficBlender:
    """
    Stealth Module.
    Wraps payloads in benign-looking traffic and adds jitter.
    """
    @staticmethod
    def blend_traffic(payload: str, protocol: str = "HTTP") -> str:
        """
        Wraps payload in protocol-specific noise.
        """
        if protocol == "HTTP":
            # Simulate a valid JSON API request
            return f'{{"jsonrpc": "2.0", "method": "query", "params": {{ "id": "{payload}" }}, "id": 1}}'
        elif protocol == "SQL":
            # Wrap in a query
            return f"SELECT * FROM logs WHERE message = '{payload}'"
        return payload

    @staticmethod
    def apply_jitter(base_delay: float = 0.1):
        """
        Randomizes timing to evade analysis.
        """
        jitter = random.uniform(0, base_delay * 2)
        time.sleep(base_delay + jitter)

class PivotTunnel:
    """
    Lateral Movement Module.
    Wraps commands to execute through a compromised host.
    UPGRADED: Stealth & Resilience.
    """
    def __init__(self, network: NetworkSim):
        self.network = network
        self.pivots = []
        self.blender = TrafficBlender()

    def add_pivot(self, host_ip: str):
        console.print(f"[PIVOT] 🌉 Established Tunnel Node: {host_ip}")
        self.pivots.append(host_ip)

    def execute_remote(self, target_ip: str, payload: str, stealth: bool = True) -> str:
        """
        Routes the attack through the last pivot with stealth.
        """
        # 1. Apply Jitter (Stealth)
        if stealth:
            self.blender.apply_jitter()

        # 2. Blend Traffic (Stealth)
        if stealth:
            final_payload = self.blender.blend_traffic(payload)
        else:
            final_payload = payload

        # 3. Resilience: Auto-Reconnect Logic
        retries = 3
        while retries > 0:
            try:
                if not self.pivots:
                    source = "INTERNET"
                else:
                    source = self.pivots[-1]
                    console.print(f"[PIVOT] 🔀 Routing: INTERNET -> {source} -> {target_ip} (Stealth={stealth})")

                response = self.network.route_packet(source, target_ip, final_payload)

                if "CONNECTION REFUSED" in response:
                    raise ConnectionError("Link Dropped")

                return response

            except ConnectionError:
                console.print(f"[PIVOT] ⚠️ Link Unstable. Retrying... ({retries} left)")
                retries -= 1
                time.sleep(0.5) # Wait for network to stabilize

        return "CONNECTION FAILURE"
