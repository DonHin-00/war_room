import re
import time
import math
from typing import Dict, Any, Optional

class ExoShield:
    """
    Component 3: ExoShield (Modern WAF/WAAP).
    Uses Intent Analysis (Entropy + Behavioral Heuristics).
    """
    def analyze_intent(self, payload: str) -> Dict[str, Any]:
        """
        Detects anomalous intent in the request.
        """
        # 1. Entropy Check (Detects Encrypted/Obfuscated Payloads)
        entropy = self._calculate_entropy(payload)
        if entropy > 4.5:
            return {"allowed": False, "reason": f"High Entropy Detected ({entropy:.2f}) - Possible Obfuscation"}

        # 2. Length Anomaly
        if len(payload) > 1000:
            return {"allowed": False, "reason": "Payload Size Exceeds Safety Limits"}

        # 3. Keyword Heuristics (SQLi / Injection)
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
    """
    def __init__(self):
        self.request_log = []
        self.blocklist = set()

    def log_request(self, source_ip: str):
        now = time.time()
        # Clean old logs (10s window)
        self.request_log = [r for r in self.request_log if now - r['time'] < 10]

        # Add new
        self.request_log.append({"ip": source_ip, "time": now})

        # Check Rate Limit (5 req / 10s)
        count = sum(1 for r in self.request_log if r['ip'] == source_ip)
        if count > 5:
            print(f"[WATCHTOWER] 🚨 FLOOD DETECTED from {source_ip}. Blocking.")
            self.blocklist.add(source_ip)

    def is_blocked(self, source_ip: str) -> bool:
        return source_ip in self.blocklist

class SecureGateway:
    """
    Component 1: SecureGateway.
    The Hardened Entry Port.
    """
    def __init__(self):
        self.shield = ExoShield()
        self.monitor = WatchtowerDaemon()

    def process_ingress(self, source_ip: str, payload: str) -> Dict[str, Any]:
        print(f"[GATEKEEPER] 🛡️ Inspecting ingress from {source_ip}...")

        # 1. Check Blocklist (Watchtower)
        if self.monitor.is_blocked(source_ip):
            return {"status": "BLOCKED", "error": "IP Blocklisted"}

        self.monitor.log_request(source_ip)

        # 2. WAF Inspection (ExoShield)
        analysis = self.shield.analyze_intent(payload)
        if not analysis["allowed"]:
            print(f"[GATEKEEPER] 🚫 REJECTED: {analysis['reason']}")
            return {"status": "REJECTED", "error": analysis['reason']}

        # 3. Pass
        print("[GATEKEEPER] ✅ Access Granted.")
        return {"status": "ACCEPTED", "payload": payload}
