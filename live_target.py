
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

PORT = 5000
BLOCKLIST_FILE = "global_blocklist.json"

class VulnerableHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.logger = utils.setup_logging("TARGET_HTTP", os.path.join(config.LOG_DIR, "target_http.log"))
        self.access_logger = logging.getLogger("ACCESS_LOG")
        self.access_logger.setLevel(logging.INFO)
        fh = logging.FileHandler(os.path.join(config.LOG_DIR, "access.log"))
        fh.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        self.access_logger.addHandler(fh)

    def is_blocked(self, client_ip):
        try:
            blocked = utils.safe_json_read(BLOCKLIST_FILE, [])
            return client_ip in blocked
        except: return False

    def log_request(self, code='-', size='-'):
        # Override to use our custom access logger for WAF parsing
        self.access_logger.info(f"{self.client_address[0]} - {self.requestline} - {code}")

    def do_GET(self):
        if self.is_blocked(self.client_address[0]):
            self.send_error(403, "Forbidden (IP Blocked by SOC)")
            return

        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)

        # Vulnerabilities
        if 'q' in params:
            query = params['q'][0]

            # SQLi Simulation
            if "UNION" in query.upper() or "SELECT" in query.upper():
                self.logger.critical(f"SQLi SUCCESS from {self.client_address[0]}")
                utils.safe_file_write(os.path.join(config.TARGET_DIR, "db_leak.csv"), "admin,hash_dump")

            # RCE Simulation (Real Execution!)
            # Dangerous signatures: ;, |, $()
            if any(c in query for c in [';', '|', '$']):
                self.logger.critical(f"RCE ATTEMPT from {self.client_address[0]}")
                # Execute safely-ish
                try:
                    # Sanitize slightly to prevent destroying the lab environment
                    # Only allow echo, id, whoami
                    if "rm " in query or "shutdown" in query:
                        self.logger.warning("RCE BLOCKED: Destructive command detected.")
                    else:
                        # Extract command (very naive)
                        cmd = query.split(';')[-1].strip()
                        if cmd:
                            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=1)
                            self.logger.info(f"RCE Output: {output.decode().strip()}")
                            utils.safe_file_write(os.path.join(config.TARGET_DIR, "rce_evidence.txt"), output.decode())
                except Exception as e:
                    self.logger.error(f"RCE Execution Failed: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Welcome to the Vulnerable Server. Proceed with caution.")

def run_server():
    # Ensure logs dir
    os.makedirs(config.LOG_DIR, exist_ok=True)

    # Initialize blocklist if missing
    if not os.path.exists(BLOCKLIST_FILE):
        utils.safe_json_write(BLOCKLIST_FILE, [])

    with socketserver.TCPServer(("", PORT), VulnerableHTTPHandler) as httpd:
        print(f"\033[93m[TARGET] HTTP Server running on port {PORT}\033[0m")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
