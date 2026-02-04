#!/usr/bin/env python3
"""
Orange Team: Education & Training.
Analyzes attacks (Red) to teach secure coding (Yellow).
Bridging the gap between Attackers and Builders.
"""

import os
import sys
import time
import json
import random
import signal
import secrets

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

# --- VISUALS ---
C_ORANGE = "\033[33m"
C_RESET = "\033[0m"

class OrangeEducator:
    def __init__(self):
        self.running = True
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)
        self.setup()

    def setup(self):
        print(f"{C_ORANGE}[SYSTEM] Orange Team (Educators) Initialized.{C_RESET}")

    def shutdown(self, signum, frame):
        print(f"\n{C_ORANGE}[SYSTEM] Orange Team workshop closed...{C_RESET}")
        self.running = False
        sys.exit(0)

    def analyze_attacks(self):
        """Read audit logs to find successful attacks."""
        if not os.path.exists(config.AUDIT_LOG): return

        attacks_detected = 0
        try:
            with open(config.AUDIT_LOG, 'r') as f:
                for line in f:
                    if "EXFILTRATION" in line or "RANSOMWARE" in line:
                        attacks_detected += 1
        except: pass

        if attacks_detected > 0:
            self.publish_standards(attacks_detected)

    def publish_standards(self, urgency_level):
        """Update coding standards based on attack intel."""
        standards = {
            "require_encryption": True,
            "input_validation": "STRICT",
            "urgency": urgency_level,
            "last_updated": time.time()
        }

        path = os.path.join(config.BASE_DIR, "intelligence", "coding_standards.json")
        try:
            utils.safe_file_write(path, json.dumps(standards, indent=4))
            # print(f"{C_ORANGE}[ORANGE] Updated Secure Coding Standards (Urgency: {urgency_level}){C_RESET}")
        except: pass

    def run_workshop(self):
        """Simulate a training session (No-op in code, but conceptually updates Yellow's behavior via file)."""
        pass

    def run(self):
        while self.running:
            try:
                self.analyze_attacks()
                time.sleep(random.uniform(5.0, 10.0))
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    bot = OrangeEducator()
    bot.run()
