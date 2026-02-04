#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield
"""

import glob
import os
import time
import random
import signal
import sys
import logging
import hashlib
import collections
from typing import Dict, Any, List, Deque, Set
import threading

import utils
import config

# Setup Logging
utils.setup_logging(config.PATHS["LOG_BLUE"])
logger = logging.getLogger("BlueTeam")

class SignatureDatabase:
    """Manages known bad file hashes (Adaptive Immunity)."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.signatures: Set[str] = set()
        self.load()

    def load(self):
        data = utils.safe_json_read(self.filepath)
        if isinstance(data, list):
            self.signatures = set(data)

    def save(self):
        utils.safe_json_write(self.filepath, list(self.signatures))

    def add_signature(self, file_content: bytes):
        file_hash = hashlib.sha256(file_content).hexdigest()
        if file_hash not in self.signatures:
            self.signatures.add(file_hash)
            self.save()
            logger.info(f"Learned new signature: {file_hash[:8]}...")

    def check_signature(self, file_content: bytes) -> bool:
        file_hash = hashlib.sha256(file_content).hexdigest()
        return file_hash in self.signatures

class BlueDefender:
    """
    The 4-Layer Adaptive SOC Controller (Emulation Mode).
    Manages sub-agents for SENSOR, ANALYZER, HUNTER, and RESPONDER roles based on frequency schedules.
    """
    def __init__(self):
        self.running = True
        self.iteration_count = 0
        self.audit_logger = utils.AuditLogger(config.PATHS["AUDIT_LOG"])
        self.state_manager = utils.StateManager(config.PATHS["WAR_STATE"])
        self.signature_db = SignatureDatabase(config.PATHS["SIGNATURES"])

        self.backups: Dict[str, bytes] = {}

        utils.limit_resources(ram_mb=config.SYSTEM["RESOURCE_LIMIT_MB"])

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def shutdown(self, signum, frame):
        logger.info("Shutting down SOC...")
        self.running = False
        sys.exit(0)

    def update_heartbeat(self):
        hb_file = os.path.join(config.PATHS["DATA_DIR"], "blue.heartbeat")
        try:
            with open(hb_file, 'w') as f: f.write(str(time.time()))
        except: pass

    # --- SOC LAYERS ---

    def layer_sensor(self):
        """Layer 1: Perimeter (DMZ) Signature Scanning."""
        mitigated = 0
        zone = config.ZONES["DMZ"]
        try:
            with os.scandir(zone) as it:
                for entry in it:
                    if entry.is_file():
                        if "c2_beacon" in entry.name or utils.scan_threats(entry.path):
                            os.remove(entry.path)
                            mitigated += 1
                            logger.info(f"[SENSOR] Neutralized threat in DMZ: {entry.name}")
        except: pass
        return mitigated

    def layer_analyzer(self):
        """Layer 2: Endpoint (USER/SERVER) Heuristic Analysis."""
        mitigated = 0
        for zone_name in ["USER", "SERVER"]:
            zone = config.ZONES[zone_name]
            try:
                with os.scandir(zone) as it:
                    for entry in it:
                        if entry.is_file() and not utils.is_tar_pit(entry.path) and not utils.is_honeypot(entry.path):
                            try:
                                if entry.name.endswith(".enc"): continue
                                entropy = utils.calculate_entropy(utils.safe_file_read(entry.path, 0.1))
                                if entropy > 3.5:
                                    os.remove(entry.path)
                                    mitigated += 1
                                    logger.info(f"[ANALYZER] Heuristic match in {zone_name}: {entry.name}")
                            except: pass
            except: pass
        return mitigated

    def layer_hunter(self):
        """Layer 3: Core (CORE) Process Hunting & Integrity."""
        mitigated = 0
        zone = config.ZONES["CORE"]
        try:
            with os.scandir(zone) as it:
                for entry in it:
                    if entry.name != "readme.txt" and not entry.name in self.backups:
                         os.remove(entry.path)
                         mitigated += 1
        except: pass

        if os.path.exists(config.PATHS["PROC"]):
             try:
                with os.scandir(config.PATHS["PROC"]) as it:
                    for entry in it:
                        os.remove(entry.path)
                        mitigated += 1
             except: pass

        return mitigated

    def layer_responder(self):
        """Layer 4: SOAR - Orchestration & Recovery."""
        mitigated = 0
        restored = 0

        # Auto Backup Core
        try:
            for entry in os.scandir(config.ZONES["CORE"]):
                if entry.is_file():
                    self.backups[entry.name] = utils.safe_file_read(entry.path)
        except: pass

        # Auto Restore Encrypted
        for zone_path in config.ZONES.values():
            try:
                for entry in os.scandir(zone_path):
                    if entry.name.endswith(".enc"):
                        orig = entry.name[:-4]
                        if orig in self.backups:
                            os.remove(entry.path)
                            with open(os.path.join(zone_path, orig), 'w') as f:
                                f.write(self.backups[orig])
                            restored += 1
            except: pass

        # Deploy Traps if missing
        for zone in config.ZONES.values():
            utils.create_tar_pit(os.path.join(zone, "sys.pipe"))

        return restored

    def engage(self):
        logger.info("Blue SOC Initialized. 4-Layer Emulation Mode.")

        while self.running:
            try:
                self.iteration_count += 1
                self.update_heartbeat()

                # SOC Cycle based on Config Frequencies
                total_mitigated = 0

                if self.iteration_count % config.EMULATION["BLUE"]["SENSOR_FREQ"] == 0:
                    total_mitigated += self.layer_sensor()

                if self.iteration_count % config.EMULATION["BLUE"]["ANALYZER_FREQ"] == 0:
                    total_mitigated += self.layer_analyzer()

                if self.iteration_count % config.EMULATION["BLUE"]["HUNTER_FREQ"] == 0:
                    total_mitigated += self.layer_hunter()

                if self.iteration_count % config.EMULATION["BLUE"]["RESPONDER_FREQ"] == 0:
                    restored = self.layer_responder()

                # Update Alert Level based on activity
                war_state = self.state_manager.get_war_state()
                current_alert = war_state.get('blue_alert_level', 1)

                if total_mitigated > 0 and current_alert < config.SYSTEM["MAX_ALERT_LEVEL"]:
                     self.state_manager.update_war_state({'blue_alert_level': min(config.SYSTEM["MAX_ALERT_LEVEL"], current_alert + 1)})

                if total_mitigated > 0:
                    logger.info(f"SOC Activity: Mitigated {total_mitigated} threats.")

                time.sleep(random.uniform(0.5, 1.5))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"SOC Loop Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    BlueDefender().engage()
