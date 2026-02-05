
import http.server
import socketserver
import urllib.parse
import os
import json
import logging
import subprocess
import utils
import config
import threading
import time
import re
import random

PORT = 5000
BLOCKLIST_FILE = "global_blocklist.json"

class SmartHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """
    A Smart Target that serves HTTP but also learns from attacks.
    It combines real HTTP handling with 'Adaptive Target' self-healing logic.
    """

    def setup(self):
        super().setup()
        self.logger = utils.setup_logging("SMART_TARGET", os.path.join(config.LOG_DIR, "target_http.log"))
        self.access_logger = logging.getLogger("ACCESS_LOG")
        if not self.access_logger.handlers:
            self.access_logger.setLevel(logging.INFO)
            fh = logging.FileHandler(os.path.join(config.LOG_DIR, "access.log"))
            fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
            self.access_logger.addHandler(fh)

    def log_request(self, code='-', size='-'):
        # WAF friendly format: IP - REQUEST - CODE - UA
        ua = self.headers.get('User-Agent', 'Unknown')
        self.access_logger.info(f"{self.client_address[0]} - {self.requestline} - {code} - {ua}")

    def is_blocked(self, client_ip, request_line):
        """Checks SOC blocklist and internal Dynamic Patches."""
        # 1. Check Global Blocklist (SOC/Blue Brain)
        try:
            blocked_ips = utils.safe_json_read(BLOCKLIST_FILE, [])
            if client_ip in blocked_ips:
                return True, "IP Blocked by SOC"
        except: pass

        # 2. Check Dynamic Patches (Self-Learning)
        # Decode request for inspection
        decoded = urllib.parse.unquote(request_line)
        for pattern in self.server.patched_patterns:
            if re.search(pattern, decoded, re.IGNORECASE):
                return True, f"Blocked by Hotfix Pattern: {pattern}"

        return False, None

    def learn_attack(self, query):
        """Crude AI: Extract a signature from the attack to block it next time."""
        # In a real system, this would be more specific.
        # Here we block high-entropy keywords found in the attack.
        if "UNION" in query.upper():
            self.server.patched_patterns.add(r"UNION")
            self.logger.info("LEARNED PATCH: Blocking 'UNION'")
        elif "SELECT" in query.upper():
            self.server.patched_patterns.add(r"SELECT")
            self.logger.info("LEARNED PATCH: Blocking 'SELECT'")
        elif "<script>" in query.lower():
            self.server.patched_patterns.add(r"<script>")
            self.logger.info("LEARNED PATCH: Blocking '<script>'")
        elif "bash" in query or "sh" in query:
            self.server.patched_patterns.add(r"(bash|sh)")
            self.logger.info("LEARNED PATCH: Blocking Shells")
        elif "etc/passwd" in query:
            self.server.patched_patterns.add(r"etc/passwd")
            self.logger.info("LEARNED PATCH: Blocking LFI")

    def do_GET(self):
        # Check Defenses
        blocked, reason = self.is_blocked(self.client_address[0], self.requestline)
        if blocked:
            self.send_error(403, f"Forbidden ({reason})")
            return

        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # --- Vulnerability Simulation ---
        if 'q' in params:
            query = params['q'][0]
            attack_successful = False

            # 1. SQLi
            if "UNION" in query.upper() or "SELECT" in query.upper():
                self.logger.critical(f"SQLi SUCCESS from {self.client_address[0]}")
                utils.safe_file_write(os.path.join(config.TARGET_DIR, "db_leak.csv"), "admin,hash_dump")
                attack_successful = True

            # 2. RCE
            if any(c in query for c in [';', '|', '$']):
                self.logger.critical(f"RCE ATTEMPT from {self.client_address[0]}")
                try:
                    # Safety Filter
                    if "rm " in query or "shutdown" in query:
                        self.logger.warning("RCE BLOCKED: Destructive command detected.")
                    else:
                        cmd = query.split(';')[-1].strip()
                        if cmd:
                            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=1)
                            self.logger.info(f"RCE Output: {output.decode().strip()}")
                            utils.safe_file_write(os.path.join(config.TARGET_DIR, "rce_evidence.txt"), output.decode())
                            attack_successful = True
                except Exception as e:
                    self.logger.error(f"RCE Execution Failed: {e}")

            # 3. XSS
            if "<script>" in query.lower():
                self.logger.warning(f"XSS Triggered from {self.client_address[0]}")
                attack_successful = True

            # --- Adaptive Response ---
            if attack_successful:
                # The server "learns" from the pain
                self.learn_attack(query)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Welcome to the Smart Adaptive Server.")

class SmartServer(socketserver.TCPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.patched_patterns = set() # Runtime memory of patches
        self.allow_reuse_address = True

def self_healing_daemon():
    """Background thread to clean up artifacts (Self-Healing)."""
    logger = utils.setup_logging("TARGET_HEALER", os.path.join(config.LOG_DIR, "target_healer.log"))
    watch_dir = config.TARGET_DIR

    while True:
        try:
            # Check for compromised files
            for f in ["backdoor.sh", "db_leak.csv", "rce_evidence.txt"]:
                path = os.path.join(watch_dir, f)
                if os.path.exists(path):
                    utils.secure_delete(path)
                    logger.info(f"SELF-HEALING: Removed artifact {f}")

            # Simulated Re-imaging / Reset if too damaged
            # (Not implemented to avoid resetting the whole lab mid-test)

        except Exception as e:
            logger.error(f"Healer Error: {e}")

        time.sleep(5)

def run_server():
    os.makedirs(config.LOG_DIR, exist_ok=True)
    os.makedirs(config.TARGET_DIR, exist_ok=True)

    # Initialize blocklist
    if not os.path.exists(BLOCKLIST_FILE):
        utils.safe_json_write(BLOCKLIST_FILE, [])

    # Start Self-Healing Thread
    t = threading.Thread(target=self_healing_daemon, daemon=True)
    t.start()

    # Start Server
    # Use SmartServer to hold state (patched_patterns)
    with SmartServer(("", PORT), SmartHTTPHandler) as httpd:
        print(f"\033[96m[SMART TARGET] Active on Port {PORT}. Adaptive Defense Online.\033[0m")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
