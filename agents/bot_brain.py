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
from agents.support.mirage import Mirage
from agents.support.gatekeeper import Gatekeeper

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "bot.log")
GATEKEEPER_STATE = os.path.join(BASE_DIR, "gatekeeper.json")
PORTS_DIR = "/tmp/ports" # Simulated open ports
PASTE_DIR = "/tmp/mock_pastes"
if not os.path.exists(PORTS_DIR):
    try: os.mkdir(PORTS_DIR)
    except: pass
if not os.path.exists(PASTE_DIR):
    try: os.mkdir(PASTE_DIR)
    except: pass

class AnomalyDetector:
    """Next-Gen AI Traffic Analyzer (2026 Edition)"""
    def __init__(self):
        self.access_history = {} # {filepath: [timestamps]}
        self.threshold = 3       # Max access events per window
        self.window = 5.0        # Time window in seconds

        # Long-Term Tracking (Slow Drip)
        self.long_term_history = {} # {filepath: count}
        self.long_term_threshold = 5
        self.long_term_window = 60.0

    def log_access(self, filepath):
        now = time.time()
        if filepath not in self.access_history:
            self.access_history[filepath] = []
        self.access_history[filepath].append(now)
        # Prune old events
        self.access_history[filepath] = [t for t in self.access_history[filepath] if t > now - self.window]

        # Long Term
        if filepath not in self.long_term_history: self.long_term_history[filepath] = []
        self.long_term_history[filepath].append(now)
        self.long_term_history[filepath] = [t for t in self.long_term_history[filepath] if t > now - self.long_term_window]

    def is_under_attack(self, filepath):
        # Burst detection: High frequency access
        burst = len(self.access_history.get(filepath, [])) > self.threshold
        # Slow Drip detection: Moderate frequency over long time
        drip = len(self.long_term_history.get(filepath, [])) > self.long_term_threshold
        return burst or drip

class BotWAF:
    def __init__(self):
        self.running = True
        self.setup_logging()
        self.ai_brain = AnomalyDetector()
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

    def deploy_poisoned_bait(self):
        """Plants bait data in the ports directory."""
        # High Fidelity Deception
        targets = {
            "customer_data.db": self.mirage.generate_user_db,
            "aws_config.ini": self.mirage.generate_aws_config,
            "legacy_api.json": lambda: '{"api_key": "PROD_KEY_999", "endpoint": "v1/legacy"}'
        }

        for fname, generator in targets.items():
            fpath = os.path.join(PORTS_DIR, fname)
            if not os.path.exists(fpath):
                try:
                    content = generator()
                    safe_file_write(fpath, content)
                    self.logger.info(f"Deployed High-Fidelity Bait: {fname}")
                except: pass

    def monitor_traffic(self):
        """Monitors access via File System Access Times (atime)."""
        try:
            if os.path.exists(PORTS_DIR):
                with os.scandir(PORTS_DIR) as entries:
                    for entry in entries:
                        if entry.is_file():
                            # Check atime (Last Access Time)
                            try:
                                stats = entry.stat()
                                # We check if atime is very recent (implied 'read' by Red Team)
                                if time.time() - stats.st_atime < 1.0:
                                    self.ai_brain.log_access(entry.path)

                                    if self.ai_brain.is_under_attack(entry.path):
                                        self.activate_shadow_ban(entry.path)
                            except: pass

            # Check Pastes for Honey Pot Cards
            if os.path.exists(PASTE_DIR):
                with os.scandir(PASTE_DIR) as entries:
                    for entry in entries:
                        if entry.is_file():
                            try:
                                with open(entry.path, 'r', errors='ignore') as f:
                                    content = f.read()
                                    if "4532015112830369" in content or "4485123456781234" in content:
                                        self.logger.warning(f"CRITICAL ALERT: Honey Pot Credit Cards detected on public paste! File: {entry.name}")
                                        os.remove(entry.path)
                            except: pass
        except: pass

    def activate_shadow_ban(self, filepath):
        """Replaces file content with junk dynamically (Shadow Banning)."""
        target_id = os.path.basename(filepath)

        if self.gatekeeper.is_banned(target_id):
            # Already banned, ensure junk is served
            try:
                safe_file_write(filepath, self.mirage.generate_junk_data())
            except: pass
            return

        self.logger.warning(f"AI WAF: Burst detected on {target_id}. Escalating to Gatekeeper.")
        self.gatekeeper.report_offense(target_id)

        try:
            # Immediate neutralization
            safe_file_write(filepath, self.mirage.generate_junk_data())
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
