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

# Adjust path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import safe_file_write

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "yellow.log")
TARGET_DIR = "/tmp"

class VulnerableApp(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.wfile.write(b"Welcome to Legacy App v1.0 (Vulnerable)")
        elif self.path.startswith("/search"):
            # Reflected XSS / Command Injection (Simulated)
            query = self.path.split("=")[-1]
            if ";" in query:
                # Command Injection Emulation: Writing to a file to prove execution
                try:
                    cmd = query.split(";")[1]
                    with open(os.path.join(TARGET_DIR, "pwned_by_yellow.txt"), "w") as f:
                        f.write(f"Executed: {cmd}")
                except: pass
            self.send_response(200)
            self.wfile.write(f"Results for: {query}".encode())
        else:
            self.send_response(404)

    def log_message(self, format, *args):
        return

class YellowBuilder:
    def __init__(self):
        self.running = True
        self.services = []
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
        self.logger = logging.getLogger("YellowTeam")

    def handle_signal(self, signum, frame):
        self.logger.info("Yellow Team shutting down services...")
        self.running = False
        for s in self.services:
            s.shutdown()

    def start_service(self, port):
        try:
            httpd = socketserver.TCPServer(("127.0.0.1", port), VulnerableApp)
            t = threading.Thread(target=httpd.serve_forever)
            t.daemon = True
            t.start()
            self.services.append(httpd)
            self.logger.info(f"Deployed Vulnerable App on port {port}")
        except Exception as e:
            self.logger.error(f"Failed to start service on {port}: {e}")

    def run(self):
        self.logger.info("Yellow Team Initialized. Building Infrastructure.")

        # Deploy initial stack
        self.start_service(8081)
        self.start_service(8082)

        while self.running:
            # Simulate "DevOps" changes
            time.sleep(10)
            if random.random() < 0.2:
                self.logger.info("Rolling out 'fix' (Restarting services)...")
                # Just a log event for now, simulating churn

            # Verify services are up
            for s in self.services:
                pass # logic to check health

if __name__ == "__main__":
    yellow = YellowBuilder()
    yellow.run()
