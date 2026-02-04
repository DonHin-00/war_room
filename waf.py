
import re
import utils
import logging
import os
import config
import urllib.parse

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

            for pattern, threat_type in self.rules:
                if re.search(pattern, decoded_req):
                    self.logger.warning(f"DETECTED {threat_type} from {ip}")
                    self.blocked_ips.add(ip)
                    # Update global blocklist
                    try:
                        current = utils.safe_json_read(config.TARGET_DIR + "/../global_blocklist.json", [])
                        if ip not in current:
                            current.append(ip)
                            utils.safe_json_write(config.TARGET_DIR + "/../global_blocklist.json", current)
                    except: pass
                    return True, ip

            return False, ip
        except: return False, None

    def update_rules(self):
        # Placeholder for dynamic rule updates
        pass
