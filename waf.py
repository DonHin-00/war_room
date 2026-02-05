
import re
import utils
import logging
import os
import config
import urllib.parse
import ai_defense

class WebApplicationFirewall:
    """Hybrid WAF (Regex + AI) for inspecting 'network' files."""
    def __init__(self):
        self.logger = utils.setup_logging("WAF", os.path.join(config.LOG_DIR, "waf.log"))

        # Load AI Engine
        try:
            self.ai_engine = ai_defense.get_classifier()
            self.logger.info("AI Defense Engine Loaded.")
        except Exception as e:
            self.logger.error(f"Failed to load AI Engine: {e}")
            self.ai_engine = None

        self.rules = [
            # SQL Injection
            (r"(?i)(SELECT|UNION|INSERT|UPDATE|DELETE|DROP).*FROM", "SQLi"),
            (r"(?i)OR\s+1=1", "SQLi"),
            (r"(?i)--", "SQLi_Comment"),
            # XSS
            (r"(?i)<script>", "XSS"),
            (r"(?i)javascript:", "XSS"),
            (r"(?i)onerror=", "XSS"),
            # RCE
            (r"(?i)(;|&|\|)\s*(sh|bash|nc|wget|curl)", "RCE"),
            # Path Traversal
            (r"\.\./", "LFI"),
        ]
        self.blocked_ips = set() # Simulated IP blocking via filename metadata

    def inspect_log_line(self, line):
        """Inspect a server access log line. Returns (malicious: bool, ip: str)."""
        # Format: IP - REQUEST - CODE (Simulated Common Log Format from live_target.py)
        # e.g., "127.0.0.1 - GET /?q=UNION... HTTP/1.1 - 200"
        try:
            parts = line.split(' - ')
            if len(parts) < 2: return False, None

            ip = parts[0]
            request = parts[1]

            # Check Blocklist
            if ip in self.blocked_ips:
                return True, ip # Already blocked

            # Check Payload
            # Decode URL encoding first
            decoded_req = urllib.parse.unquote(request)

            # 1. Signature Check (Fast)
            for pattern, threat_type in self.rules:
                if re.search(pattern, decoded_req):
                    self._block_ip(ip, f"Signature: {threat_type}")
                    return True, ip

            # 2. AI Anomaly Check (Heuristic)
            if self.ai_engine:
                label, scores = self.ai_engine.predict(decoded_req)
                if label == 'malicious':
                    confidence = scores['malicious'] - scores['benign']
                    # Heuristic threshold: if gap is significant (> 2.0 roughly means 7x more likely)
                    if confidence > 1.0:
                        self.logger.warning(f"AI DETECTED ANOMALY (Conf: {confidence:.2f}) from {ip}")
                        self._block_ip(ip, "AI_Anomaly_Detection")
                        return True, ip

            return False, ip
        except: return False, None

    def _block_ip(self, ip, reason):
        self.logger.warning(f"BLOCKING {ip} Reason: {reason}")
        self.blocked_ips.add(ip)
        try:
            current = utils.safe_json_read(config.TARGET_DIR + "/../global_blocklist.json", [])
            if ip not in current:
                current.append(ip)
                utils.safe_json_write(config.TARGET_DIR + "/../global_blocklist.json", current)
        except: pass

    def update_rules(self):
        # Placeholder for dynamic rule updates
        pass
