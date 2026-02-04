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

# Adjust path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import safe_file_read, safe_file_write

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "bot.log")
PORTS_DIR = "/tmp/ports" # Simulated open ports
PASTE_DIR = "/tmp/mock_pastes"
if not os.path.exists(PORTS_DIR):
    try: os.mkdir(PORTS_DIR)
    except: pass
if not os.path.exists(PASTE_DIR):
    try: os.mkdir(PASTE_DIR)
    except: pass

class BotWAF:
    def __init__(self):
        self.running = True
        self.setup_logging()
        self.banned_ips = [] # In simulation, we might ban by ignoring specific file patterns

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

    def deploy_poisoned_bait(self):
        """Plants bait data in the ports directory."""
        baits = ["customer_data.db", "admin_creds.xml", "api_keys.json"]
        for b in baits:
            fname = os.path.join(PORTS_DIR, b)
            if not os.path.exists(fname):
                try:
                    # Poisoned content: tracking tokens
                    content = f"TRACKING_TOKEN_{random.randint(1000,9999)}"
                    safe_file_write(fname, content)
                    self.logger.info(f"Deployed poisoned bait: {b}")
                except: pass

    def monitor_traffic(self):
        """Monitors access to ports and mock pastes."""
        try:
            # Check Pastes for Honey Pot Cards
            if os.path.exists(PASTE_DIR):
                with os.scandir(PASTE_DIR) as entries:
                    for entry in entries:
                        if entry.is_file():
                            try:
                                with open(entry.path, 'r', errors='ignore') as f:
                                    content = f.read()
                                    # Check for our specific honey pot tokens
                                    if "4532015112830369" in content or "4485123456781234" in content:
                                        self.logger.warning(f"CRITICAL ALERT: Honey Pot Credit Cards detected on public paste! File: {entry.name}")
                                        # "Take down" the paste
                                        os.remove(entry.path)
                            except: pass
        except: pass

    def run(self):
        self.logger.info("Bot WAF Initialized. Guarding Ports.")

        while self.running:
            try:
                self.deploy_poisoned_bait()
                self.monitor_traffic()

                # Simulate WAF logic: Randomly 'rotate' ports (delete and recreate dir) to confuse attackers
                if random.random() < 0.05:
                    self.logger.info("Rotating encryption keys (Simulated Port Rotation)...")
                    # No actual action needed for this sim level, just flavor/logging

                time.sleep(2.0)
            except Exception as e:
                self.logger.error(f"WAF Error: {e}")
                time.sleep(1)

        self.logger.info("Bot WAF Shutdown.")

if __name__ == "__main__":
    bot = BotWAF()
    bot.run()
