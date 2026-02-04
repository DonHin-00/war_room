import re
import time
import math
from typing import Dict, Any, Optional
from ant_swarm.support.external_storage import LongTermDrive

class ExoShield:
    def analyze_intent(self, payload: str) -> Dict[str, Any]:
        entropy = self._calculate_entropy(payload)
        if entropy > 4.5:
            return {"allowed": False, "reason": f"High Entropy Detected ({entropy:.2f}) - Possible Obfuscation"}
        if len(payload) > 1000:
            return {"allowed": False, "reason": "Payload Size Exceeds Safety Limits"}
        danger_keywords = ["UNION SELECT", "DROP TABLE", "javascript:", "vbscript:", "<script>"]
        for kw in danger_keywords:
            if kw.lower() in payload.lower():
                return {"allowed": False, "reason": f"Malicious Keyword Detected: {kw}"}
        return {"allowed": True, "reason": "Clean"}

    def _calculate_entropy(self, text: str) -> float:
        if not text: return 0
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

class WatchtowerDaemon:
    """
    Component 2: WatchtowerDaemon.
    Monitors traffic and detects DoS/Flooding.
    REINFORCED: Uses Persistent Storage.
    """
    def __init__(self, storage: LongTermDrive):
        self.storage = storage
        self.request_log = []

    def log_request(self, source_ip: str):
        now = time.time()
        self.request_log = [r for r in self.request_log if now - r['time'] < 10]
        self.request_log.append({"ip": source_ip, "time": now})

        # Check Rate Limit (5 req / 10s)
        count = sum(1 for r in self.request_log if r['ip'] == source_ip)
        if count > 5:
            print(f"[WATCHTOWER] 🚨 FLOOD DETECTED from {source_ip}. Issuing Strike.")
            self.storage.add_strike(source_ip)

    def is_blocked(self, source_ip: str) -> bool:
        # Check persistent reputation
        status = self.storage.get_ip_status(source_ip)
        if status["ban_expiry"] > time.time():
            return True
        return False

class SecureGateway:
    """
    Component 1: SecureGateway.
    The Hardened Entry Port.
    """
    def __init__(self, storage: LongTermDrive = None):
        # Allow injection or default
        if not storage: storage = LongTermDrive()
        self.shield = ExoShield()
        self.monitor = WatchtowerDaemon(storage)

    def process_ingress(self, source_ip: str, payload: str) -> Dict[str, Any]:
        print(f"[GATEKEEPER] 🛡️ Inspecting ingress from {source_ip}...")

        # 1. Check Persistent Blocklist
        if self.monitor.is_blocked(source_ip):
            print(f"[GATEKEEPER] ⛔ REJECTED: IP {source_ip} is currently BANNED.")
            return {"status": "BLOCKED", "error": "IP Blocklisted"}

        self.monitor.log_request(source_ip)

        # 2. WAF Inspection
        analysis = self.shield.analyze_intent(payload)
        if not analysis["allowed"]:
            print(f"[GATEKEEPER] 🚫 REJECTED: {analysis['reason']}")
            # Add Strike for Malicious Payload
            self.monitor.storage.add_strike(source_ip)
            return {"status": "REJECTED", "error": analysis['reason']}

        # 3. Pass
        print("[GATEKEEPER] ✅ Access Granted.")
        return {"status": "ACCEPTED", "payload": payload}
