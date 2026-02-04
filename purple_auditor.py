#!/usr/bin/env python3
"""
Purple Auditor (Referee)
Continuous integrity monitoring and simulation balancing.
Ensures the Red/Blue ecosystem remains healthy, safe, and active.
"""

import time
import os
import sqlite3
import logging
import subprocess
import config
from db_manager import DatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [PURPLE REF] - %(message)s')

class PurpleAuditor:
    def __init__(self):
        self.db = DatabaseManager()
        self.running = True
        self.metrics = {"red_events": 0, "blue_events": 0}

    def check_health(self):
        """Verifies Red/Blue agents are alive using ps."""
        red_alive = False
        blue_alive = False

        try:
            # Check using pgrep/ps instead of psutil to avoid external deps
            output = subprocess.check_output(["ps", "aux"], text=True)
            if "red_brain.py" in output: red_alive = True
            if "blue_brain.py" in output: blue_alive = True
        except: pass

        if not red_alive:
            logging.warning("CRITICAL: Red Team is offline!")
        if not blue_alive:
            logging.warning("CRITICAL: Blue Team is offline!")

        return red_alive and blue_alive

    def audit_database(self):
        """Checks DB integrity and Threat Feed population."""
        count = self.db.count_iocs()
        if count < 100:
            logging.warning(f"Low Threat Intel Count: {count}. Feed fetch recommended.")
        else:
            logging.info(f"Threat Intel Database Healthy: {count} IOCs.")

    def audit_lab(self):
        """Verifies Malware Lab Output."""
        required = ["stix_synthetic_beacons.json", "stix_real_hashes.json"]
        for f in required:
            if not os.path.exists(f):
                logging.warning(f"Lab Artifact Missing: {f}")
            else:
                size = os.path.getsize(f)
                if size < 100:
                    logging.warning(f"Lab Artifact Empty/Small: {f}")

    def enforce_safety(self):
        """Ensures no processes are escaping simulation constraints."""
        # Example: Check for fork bombs or excessive PIDs
        # Check if /tmp/ is getting full of artifacts
        artifacts = [f for f in os.listdir("/tmp") if f.startswith("malware_") or f.endswith(".cron")]
        if len(artifacts) > 50:
            logging.warning(f"High Artifact Count ({len(artifacts)}). Cleaning up...")
            for f in artifacts:
                try: os.remove(os.path.join("/tmp", f))
                except: pass

    def run(self):
        logging.info("Purple Auditor Active. Monitoring Simulation...")
        while self.running:
            try:
                self.check_health()
                self.audit_database()
                self.audit_lab()
                self.enforce_safety()
                time.sleep(10)
            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logging.error(f"Auditor Error: {e}")
                time.sleep(5)

if __name__ == "__main__":
    ref = PurpleAuditor()
    ref.run()
