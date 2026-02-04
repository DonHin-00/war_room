#!/usr/bin/env python3
"""
Blue Brain (Hunter Edition)
Advanced Active Defense
"""

import time
import random
import logging
import signal
import os
from threat_intel import ThreatIntel
from blue_tools import ProcessAuditor, BeaconHunter, ArtifactScanner
from db_manager import DatabaseManager
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BLUE HUNTER] - %(message)s')

class BlueHunter:
    def __init__(self):
        self.db = DatabaseManager()
        self.ti = ThreatIntel()
        self.proc_audit = ProcessAuditor()
        self.net_hunt = BeaconHunter()
        self.artifact_scan = ArtifactScanner()
        self.running = True

    def remediate_process(self, pid, reason):
        try:
            if pid < 1000: return # Safety check
            os.kill(pid, signal.SIGKILL)
            logging.warning(f"TERMINATED PID {pid} [{reason}]")
            self.db.log_event("BLUE", "KILL", f"PID {pid} - {reason}")
        except: pass

    def remediate_artifact(self, path):
        try:
            os.remove(path)
            logging.warning(f"REMOVED Artifact: {path}")
            self.db.log_event("BLUE", "CLEAN", path)
        except: pass

    def run(self):
        logging.info("Blue Hunter Active. Monitoring...")

        while self.running:
            try:
                # 1. Network Hunting (IOC Check)
                threats = self.net_hunt.analyze_network(self.ti)
                for t in threats:
                    self.remediate_process(t['pid'], f"Network Connection to {t['ip']}")

                # 2. Process Auditing (Diskless/Suspicious)
                procs = self.proc_audit.scan_proc()
                for p in procs:
                    # Heuristic: only kill if we are sure, or just log?
                    # For this war room, we kill.
                    self.remediate_process(p['pid'], p['reason'])

                # 3. Artifact Scanning (Persistence)
                artifacts = self.artifact_scan.scan_persistence()
                for a in artifacts:
                    self.remediate_artifact(a)

                time.sleep(2) # Scan interval

            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logging.error(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    hunter = BlueHunter()
    hunter.run()
