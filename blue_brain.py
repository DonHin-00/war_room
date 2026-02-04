#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield

This module implements the Blue Team Agent in "Detection Mode".
It focuses on scanning, logging, and restoring systems based on fixed policies.
"""

import glob
import os
import time
import random
import signal
import sys
import logging
import collections
from typing import Dict, Any, List

import utils
import config

# Setup Logging
utils.setup_logging(config.PATHS["LOG_BLUE"])
logger = logging.getLogger("BlueTeam")

class BlueDefender:
    """
    The Blue Team Detection & Response Agent.
    """
    def __init__(self):
        self.running = True
        self.audit_logger = utils.AuditLogger(config.PATHS["AUDIT_LOG"])
        self.backups: Dict[str, bytes] = {}

        # Enforce Limits
        utils.limit_resources(ram_mb=config.SYSTEM["RESOURCE_LIMIT_MB"])

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        logger.info("Shutting down detection...")
        self.running = False
        sys.exit(0)

    # --- TACTICS ---

    def scan_signatures(self):
        """Scans for known bad files (e.g. C2 Beacons)."""
        mitigated = 0
        if not os.path.exists(config.PATHS["WAR_ZONE"]): return {"mitigated": 0}

        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file():
                        # Simple signature: C2 Beacon filename or content
                        if "c2_beacon" in entry.name:
                            os.remove(entry.path)
                            mitigated += 1
                        elif utils.scan_threats(entry.path): # YARA-mock
                            os.remove(entry.path)
                            mitigated += 1
        except: pass
        return {"mitigated": mitigated}

    def scan_heuristics(self):
        """Scans for high entropy files (obfuscated malware)."""
        mitigated = 0
        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file() and not utils.is_tar_pit(entry.path) and not utils.is_honeypot(entry.path):
                        try:
                            # Skip known encrypted files (ransomware), handle them in RESTORE
                            if entry.name.endswith(".enc"): continue

                            entropy = utils.calculate_entropy(utils.safe_file_read(entry.path, 0.1))
                            if entropy > 3.5:
                                os.remove(entry.path)
                                mitigated += 1
                        except: pass
        except: pass
        return {"mitigated": mitigated}

    def backup_critical(self):
        """Backs up 'critical' files."""
        count = 0
        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file() and not entry.name.endswith(".enc"):
                        # Backup everything that looks safe
                        if not utils.is_tar_pit(entry.path) and not "malware" in entry.name:
                            try:
                                self.backups[entry.name] = utils.safe_file_read(entry.path)
                                count += 1
                            except: pass
        except: pass
        return {"backed_up": count}

    def restore_data(self):
        """Restores encrypted files from backup."""
        restored = 0
        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file() and entry.name.endswith(".enc"):
                        original_name = entry.name[:-4] # Remove .enc
                        if original_name in self.backups:
                            os.remove(entry.path)
                            with open(os.path.join(config.PATHS["WAR_ZONE"], original_name), 'w') as f:
                                f.write(self.backups[original_name]) # Write string (safe_read returns str)
                            restored += 1
        except: pass
        return {"restored": restored}

    def deploy_defenses(self):
        """Deploys passive defenses."""
        if not os.path.exists(config.PATHS["WAR_ZONE"]): return {}
        utils.create_tar_pit(os.path.join(config.PATHS["WAR_ZONE"], "access.log"))
        utils.create_logic_bomb(os.path.join(config.PATHS["WAR_ZONE"], "shadow_backup"))
        return {"status": "deployed"}

    def engage(self):
        logger.info("Blue Team Detection Initialized. Policy: Active Defense.")

        # Initial Setup
        self.deploy_defenses()

        while self.running:
            try:
                # Detection Logic: Cycle through tasks
                actions = [
                    (self.scan_signatures, 0.4),
                    (self.scan_heuristics, 0.3),
                    (self.backup_critical, 0.2),
                    (self.restore_data, 0.1)
                ]

                func, _ = random.choices(actions, weights=[w for _, w in actions], k=1)[0]
                name = func.__name__.upper()

                result = func()

                # Log interesting events
                if result.get("mitigated", 0) > 0 or result.get("restored", 0) > 0:
                    self.audit_logger.log_event("BLUE", name, result)
                    logger.info(f"Action: {name} | Result: {result}")

                time.sleep(random.uniform(0.5, 1.5))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    BlueDefender().engage()
