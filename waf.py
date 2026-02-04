
import re
import utils
import logging
import os
import config

class WebApplicationFirewall:
    """Simulated WAF for inspecting 'network' files."""
    def __init__(self):
        self.logger = utils.setup_logging("WAF", os.path.join(config.LOG_DIR, "waf.log"))
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

    def inspect_request(self, filepath):
        """Inspect a request file. Returns (allowed: bool, reason: str)."""
        try:
            filename = os.path.basename(filepath)

            # 1. IP Reputation (Simulated by filename convention: http_req_{IP}_{ID}.log)
            # Format: http_req_192.168.1.5_12345.log
            parts = filename.split('_')
            if len(parts) >= 3:
                ip = parts[2]
                if ip in self.blocked_ips:
                    return False, f"IP_BLOCKED:{ip}"

            # 2. Payload Inspection
            content = utils.safe_file_read(filepath)
            if not content: return True, "EMPTY"

            for pattern, threat_type in self.rules:
                if re.search(pattern, content):
                    # Block and ban IP
                    if len(parts) >= 3:
                        self.blocked_ips.add(parts[2])

                    self.logger.warning(f"BLOCKED {threat_type} in {filename}")
                    return False, threat_type

            return True, "CLEAN"

        except Exception as e:
            self.logger.error(f"WAF Error inspecting {filepath}: {e}")
            return False, "ERROR"

    def update_rules(self):
        # Placeholder for dynamic rule updates
        pass
