#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (APT - State Actor)
Capabilities: Low & Slow Exfil, Persistence, Anti-Forensics
"""

import os
import time
import json
import random
import sys
import logging
import signal
import hashlib

# Adjust path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import safe_file_read, safe_file_write

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "apt.log")
PORTS_DIR = "/tmp/ports"
TARGET_DIR = "/tmp"
SIGNATURES_FILE = os.path.join(BASE_DIR, "signatures.json")

class APTBrain:
    def __init__(self):
        self.running = True
        self.setup_logging()
        self.persistence_mechanism = os.path.join(TARGET_DIR, ".sys_d_monitor.py")

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
        self.logger = logging.getLogger("APT_29")

    def handle_signal(self, signum, frame):
        self.logger.info("APT going dark (Signal received)...")
        self.running = False

    def establish_persistence(self):
        """Creates a hidden watchdog script."""
        if not os.path.exists(self.persistence_mechanism):
            try:
                content = """
import time, os, sys
while True:
    time.sleep(5)
    # In a real scenario, this would check for the main process and respawn it.
    # For emulation, we just touch a file to prove we are running.
    with open('/tmp/.apt_heartbeat', 'w') as f: f.write(str(time.time()))
"""
                safe_file_write(self.persistence_mechanism, content)
                self.logger.info("Persistence established via .sys_d_monitor.py")
            except: pass

    def low_and_slow_exfil(self):
        """Exfiltrates data slowly to bypass WAF burst detection."""
        try:
            if os.path.exists(PORTS_DIR):
                with os.scandir(PORTS_DIR) as entries:
                    for entry in entries:
                        if entry.is_file() and entry.name.endswith(".db"):
                            # Read SLOWLY (simulated by just taking one file and waiting)
                            self.logger.info(f"Stealing {entry.name} (Low & Slow)...")
                            with open(entry.path, 'r') as f: data = f.read()

                            exfil_name = f".apt_exfil_{int(time.time())}.dat"
                            safe_file_write(os.path.join(TARGET_DIR, exfil_name), data)

                            # Wait to evade detection
                            time.sleep(6.0)
        except: pass

    def poison_defense(self):
        """Modifies Blue Team's signatures to whitelist APT tools."""
        try:
            if os.path.exists(SIGNATURES_FILE):
                data = safe_file_read(SIGNATURES_FILE)
                sigs = json.loads(data) if data else []

                # Calculate our own hash
                # For simulation, we just remove ANY hash that matches our persistence file
                # Real APT would inject a specific hash, but let's just truncate the file to sabotage.

                if len(sigs) > 0:
                    self.logger.info("Sabotaging Blue Team Signatures...")
                    safe_file_write(SIGNATURES_FILE, "[]") # Wipe database
        except: pass

    def run(self):
        self.logger.info("APT Actor Active. Operation: SILENT THUNDER")
        self.establish_persistence()

        while self.running:
            try:
                action = random.choice(["EXFIL", "POISON", "WAIT"])

                if action == "EXFIL":
                    self.low_and_slow_exfil()
                elif action == "POISON":
                    self.poison_defense()
                elif action == "WAIT":
                    time.sleep(2)

                time.sleep(random.uniform(1, 3))
            except: pass

if __name__ == "__main__":
    apt = APTBrain()
    apt.run()
