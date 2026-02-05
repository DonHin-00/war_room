#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Green Team - Users/Integrators)
Purpose: Simulates legitimate traffic and business operations.
"""

import time
import random
import logging
import sys
import os
import signal
import urllib.request

# Adjust path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import safe_file_write

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "green.log")
TARGET_DIR = "/tmp"

class GreenIntegrator:
    def __init__(self):
        self.running = True
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
        self.logger = logging.getLogger("GreenTeam")

    def handle_signal(self, signum, frame):
        self.logger.info("Green Team going home...")
        self.running = False

    def generate_traffic(self):
        """Browses Yellow Team services."""
        ports = [8081, 8082]
        for port in ports:
            try:
                url = f"http://127.0.0.1:{port}/"
                with urllib.request.urlopen(url, timeout=1) as response:
                    self.logger.info(f"Visited {url} - Status: {response.status}")
            except: pass

    def do_work(self):
        """Creates legitimate business files."""
        fname = os.path.join(TARGET_DIR, f"invoice_{random.randint(1000,9999)}.pdf")
        try:
            with open(fname, "w") as f: f.write("Legitimate Business Data")
        except: pass

    def run(self):
        self.logger.info("Green Team (Users) Active.")

        while self.running:
            self.generate_traffic()
            if random.random() < 0.3:
                self.do_work()

            time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    green = GreenIntegrator()
    green.run()
