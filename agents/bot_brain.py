#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Bot/WAF)
Description: Next-Gen WAF and Load Balancer. Monitors 'ports' and manages poisoned bait.
"""

import os
import time
import json
import random
import signal
import sys
import logging
import threading
import http.server
import socketserver
import urllib.request

# Adjust path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import safe_file_read, safe_file_write
from agents.support.mirage import Mirage
from agents.support.gatekeeper import Gatekeeper

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "bot.log")
GATEKEEPER_STATE = os.path.join(BASE_DIR, "gatekeeper.json")
WAF_PORT = 9000
BACKEND_PORT = 8081

class WAFProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def handle_request(self, method):
        # 1. Inspection (WAF Logic)
        if ";" in self.path or "' OR" in self.path or "UNION" in self.path:
            self.server.waf_instance.logger.warning(f"BLOCKED MALICIOUS REQUEST: {self.path}")
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"WAF BLOCK: SQLi/RCE Detected.")
            return

        # 2. Forwarding (Reverse Proxy)
        try:
            target_url = f"http://127.0.0.1:{BACKEND_PORT}{self.path}"
            # self.server.waf_instance.logger.info(f"Forwarding to {target_url}")

            with urllib.request.urlopen(target_url, timeout=2) as resp:
                self.send_response(resp.status)
                for k, v in resp.getheaders():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())

        except Exception as e:
            self.send_response(502)
            self.end_headers()
            self.wfile.write(f"Bad Gateway: {e}".encode())

    def log_message(self, format, *args):
        return

class BotWAF:
    def __init__(self):
        self.running = True
        self.setup_logging()
        self.mirage = Mirage()
        self.gatekeeper = Gatekeeper(GATEKEEPER_STATE, self.logger)

        # Signal Handling
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
        self.logger = logging.getLogger("BotWAF")

    def handle_signal(self, signum, frame):
        self.logger.info(f"Received signal {signum}. Shutting down...")
        self.running = False
        if hasattr(self, 'httpd'):
            self.httpd.shutdown()

    def run(self):
        self.logger.info(f"Bot WAF (Reverse Proxy) listening on port {WAF_PORT}...")

        try:
            self.httpd = socketserver.TCPServer(("127.0.0.1", WAF_PORT), WAFProxyHandler)
            self.httpd.waf_instance = self

            t = threading.Thread(target=self.httpd.serve_forever)
            t.daemon = True
            t.start()

            while self.running:
                time.sleep(1)

        except Exception as e:
            self.logger.error(f"WAF Startup Failed: {e}")

        self.logger.info("Bot WAF Shutdown.")

if __name__ == "__main__":
    bot = BotWAF()
    bot.run()
