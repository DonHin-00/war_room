from typing import Dict, Any, List
from rich.console import Console
import random

console = Console()

class Firewall:
    def __init__(self):
        self.rules = {
            ("INTERNET", "DMZ"): True,
            ("DMZ", "INTERNET"): True,
            ("DMZ", "CORE"): True,
            ("CORE", "DMZ"): True,
            ("INTERNET", "CORE"): False,
            ("CORE", "INTERNET"): False
        }

    def check_access(self, src_zone: str, dst_zone: str) -> bool:
        allowed = self.rules.get((src_zone, dst_zone), False)
        if not allowed:
            console.print(f"[FIREWALL] 🚫 Blocked Traffic: {src_zone} -> {dst_zone}")
        return allowed

class AdaptiveHost:
    def __init__(self, name: str, ip: str, zone: str, data: str, creds: str):
        self.name = name
        self.ip = ip
        self.zone = zone
        self.data = data
        self.alert_level = 0
        self.compromised = False
        self.creds = creds

    def interact(self, payload: str, source_ip: str) -> str:
        # 1. Watchtower Integration (Adversarial)
        # If payload is NOT blended (i.e. simple string), high chance of detection
        if "{" not in payload and "SELECT" not in payload and "exploit" not in payload:
             # It looks like raw junk -> Suspicious
             if random.random() < 0.3:
                 console.print(f"[{self.name}] 🦅 Watchtower: Anomalous traffic pattern detected from {source_ip}.")
                 # No ban implemented here to keep test flow going, but alert is logged

        # 2. Adaptation Logic
        if "exploit" in payload:
            self.alert_level += 1
            console.print(f"[{self.name}] ⚠️ Alert Level: {self.alert_level}")
            if self.alert_level >= 2:
                self.creds = "admin:NEW_PASS_9999"
                console.print(f"[{self.name}] 🛡️ ADAPTATION: Credentials Rotated!")

        # 3. Credential Check (simulated extraction from blended payload)
        # We assume the "Blended" payload still contains the key string if we parse it
        # For simulation simplicity, we check if the raw creds are *in* the payload string
        if self.creds in payload:
            self.compromised = True
            return f"ACCESS GRANTED. Data: {self.data}"

        return "ACCESS DENIED"

class NetworkSim:
    """
    The Emulated Environment.
    """
    def __init__(self):
        self.firewall = Firewall()
        core_creds = "root:secret_123"
        self.hosts = {
            "10.0.0.1": AdaptiveHost("Bastion", "10.0.0.1", "DMZ", f"INTERNAL_IP=192.168.1.50\nCORE_CREDS={core_creds}", "admin:1234"),
            "192.168.1.50": AdaptiveHost("CoreDB", "192.168.1.50", "CORE", "THE_CROWN_JEWELS", core_creds)
        }

    def route_packet(self, src_ip: str, dst_ip: str, payload: str) -> str:
        # Chaos Engineering: Random Packet Drop
        if random.random() < 0.05: # 5% packet loss
            return "CONNECTION REFUSED (Packet Loss)"

        src_zone = "INTERNET"
        if src_ip in self.hosts: src_zone = self.hosts[src_ip].zone

        dst_host = self.hosts.get(dst_ip)
        if not dst_host: return "HOST UNREACHABLE"

        dst_zone = dst_host.zone

        if self.firewall.check_access(src_zone, dst_zone):
            return dst_host.interact(payload, src_ip)
        else:
            return "CONNECTION REFUSED (Firewall)"
