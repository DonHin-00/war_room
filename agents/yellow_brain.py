#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Yellow Team - Builder)
Purpose: Builds/Runs vulnerable infrastructure (Attack Surface).
"""

import http.server
import socketserver
import threading
import time
import random
import logging
import sys
import os
import signal
import subprocess

# Adjust path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import safe_file_write

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "yellow.log")
TARGET_DIR = "/tmp"

class AppHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.wfile.write(b"Enterprise App v2.0 (Stable)")
        elif self.path == "/health":
            self.send_response(200)
            self.wfile.write(b"OK")
        elif self.path.startswith("/search"):
            # Patched version (Simulated)
            query = self.path.split("=")[-1]
            result = f"Results: {query}"

            if ";" in query and not hasattr(self.server, "patched"):
                # Vulnerable if NOT patched - Active RCE
                try:
                    cmd = query.split(";")[1].strip()
                    # Sandbox: Only allow echo/whoami/ls
                    if cmd.startswith(("echo", "whoami", "ls")):
                        output = subprocess.check_output(cmd, shell=True, timeout=1).decode()
                        result += f"\n[RCE OUTPUT]: {output}"
                except Exception as e:
                    result += f"\n[RCE ERROR]: {e}"

            self.send_response(200)
            self.wfile.write(result.encode())
        else:
            self.send_response(404)

    def log_message(self, format, *args):
        return

class YellowSRE:
    def __init__(self):
        self.running = True
        self.services = {} # {port: server_obj}
        self.metrics = {"traffic": 0, "errors": 0}
        self.setup_logging()

        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("YellowSRE")

    def handle_signal(self, signum, frame):
        self.logger.info("Yellow SRE shutting down infrastructure...")
        self.running = False
        for s in self.services.values():
            s.shutdown()

    def deploy_service(self, port, patched=False):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", port), AppHandler)
            if patched: httpd.patched = True

            t = threading.Thread(target=httpd.serve_forever)
            t.daemon = True
            t.start()
            self.services[port] = httpd
            status = "PATCHED" if patched else "LEGACY"
            self.logger.info(f"Deployed Service ({status}) on port {port}")
        except Exception as e:
            self.logger.error(f"Failed to deploy on {port}: {e}")

    def scale_up(self):
        # Find next available port
        for p in range(8083, 8090):
            if p not in self.services:
                self.logger.info("High Load Detected! Scaling Up...")
                self.deploy_service(p, patched=True) # Always scale with patched version
                break

    def patch_vulnerabilities(self):
        # Restart all LEGACY services with PATCHED version
        ports = list(self.services.keys())
        for p in ports:
            srv = self.services[p]
            if not hasattr(srv, "patched"):
                self.logger.info(f"Patching vulnerability on Port {p}...")
                srv.shutdown()
                self.deploy_service(p, patched=True)

    def monitor_infrastructure(self):
        # Simulated Monitoring (In real scenario, check metrics endpoint)
        # Here we verify if processes/threads are alive
        for p, srv in list(self.services.items()):
            pass # Socket check logic implied by library

    def run(self):
        self.logger.info("Yellow SRE Active. Priorities: Availability, Resilience, Security.")

        # Initial Deployment (1 Legacy, 1 Patched)
        self.deploy_service(8081, patched=False)
        self.deploy_service(8082, patched=True)

        while self.running:
            self.monitor_infrastructure()

            # Random events triggering SRE actions
            event = random.random()
            if event < 0.1:
                self.scale_up()
            elif event < 0.2:
                self.patch_vulnerabilities()

            time.sleep(5)

if __name__ == "__main__":
    yellow = YellowSRE()
    yellow.run()
