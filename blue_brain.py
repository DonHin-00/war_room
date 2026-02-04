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
import ml_engine

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
    The 4-Layer Adaptive SOC Controller.
    Manages sub-agents for SENSOR, ANALYZER, HUNTER, and RESPONDER roles.
    """
    def __init__(self):
        self.running = True
        self.audit_logger = utils.AuditLogger(config.PATHS["AUDIT_LOG"])
        self.state_manager = utils.StateManager(config.PATHS["WAR_STATE"])
        self.signature_db = SignatureDatabase(config.PATHS["SIGNATURES"])

        self.ai = ml_engine.DoubleQLearner(config.BLUE["ACTIONS"], "BLUE")
        self.backups: Dict[str, bytes] = {}

        utils.limit_resources(ram_mb=config.SYSTEM["RESOURCE_LIMIT_MB"])

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def load_memory(self):
        data = self.state_manager.load_json(config.PATHS["Q_TABLE_BLUE"])
        self.ai.load(data)
        logger.info(f"AI Memory Loaded.")

    def sync_memory(self):
        data = self.ai.export()
        self.state_manager.save_json(config.PATHS["Q_TABLE_BLUE"], data)

    def shutdown(self, signum, frame):
        logger.info("Shutting down SOC...")
        self.sync_memory()
        self.running = False
        sys.exit(0)

    def update_heartbeat(self):
        hb_file = os.path.join(config.PATHS["DATA_DIR"], "blue.heartbeat")
        try:
            with open(hb_file, 'w') as f: f.write(str(time.time()))
        except: pass

    # --- SOC LAYERS (Implemented as Methods for simplicity in single process) ---

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
        # Check Core Integrity
        zone = config.ZONES["CORE"]
        compromised = False
        try:
            with os.scandir(zone) as it:
                for entry in it:
                    # Simplified integrity: core files shouldn't change
                    # If we see unknown files, delete
                    if entry.name != "readme.txt" and not entry.name in self.backups:
                         # Assume malicious if not recognized
                         os.remove(entry.path)
                         mitigated += 1
                         compromised = True
        except: pass

        # Hunt Processes
        if os.path.exists(config.PATHS["PROC"]):
             try:
                with os.scandir(config.PATHS["PROC"]) as it:
                    for entry in it:
                        os.remove(entry.path) # Kill all unknown PIDs
                        mitigated += 1
             except: pass

        return mitigated

    def layer_responder(self, action):
        """Layer 4: SOAR - Orchestration & Recovery."""
        mitigated = 0
        restored = 0

        if action == "BACKUP_CRITICAL":
            # Backup Core files
            try:
                for entry in os.scandir(config.ZONES["CORE"]):
                    if entry.is_file():
                        self.backups[entry.name] = utils.safe_file_read(entry.path)
            except: pass
            return {"backed_up": 1}

        elif action == "RESTORE_DATA":
            # Restore all zones
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
            return {"restored": restored}

        elif action == "DEPLOY_TRAP":
            for zone in config.ZONES.values():
                utils.create_tar_pit(os.path.join(zone, "sys.pipe"))
            return {"status": "traps_deployed"}

        elif action == "ISOLATE_ZONE":
            # Simulated isolation: Change permissions?
            # Or just boost alert level
            return {"status": "isolated"}

        return {}

    def engage(self):
        logger.info("Blue SOC Initialized. 4-Layer Adaptive Defense.")
        self.load_memory()

        while self.running:
            try:
                self.update_heartbeat()

                # 1. Perceive State
                war_state = self.state_manager.get_war_state()
                current_alert = war_state.get('blue_alert_level', 1)

                # 2. SOC Operations (Layers 1-3 run autonomously)
                sensor_kills = self.layer_sensor()
                analyzer_kills = self.layer_analyzer()
                hunter_kills = self.layer_hunter()

                total_mitigated = sensor_kills + analyzer_kills + hunter_kills

                # 3. Decision (Layer 4 - Responder)
                # RL controls the high-level response strategy
                state_vector = f"{current_alert}_{total_mitigated}"
                context = {"alert_level": current_alert, "mitigated": total_mitigated, "has_backup": bool(self.backups)}

                action_name = self.ai.choose_action(state_vector, context)

                # Execute Layer 4 Action
                result = self.layer_responder(action_name)

                # 4. Learning & Updates
                reward = total_mitigated * config.BLUE["REWARDS"]["MITIGATION"]
                if result.get("restored", 0) > 0: reward += config.BLUE["REWARDS"]["RESTORE_SUCCESS"]

                self.ai.memory.push(state_vector, action_name, reward, state_vector, False)
                self.ai.learn()

                # Update Alert Level based on activity
                if total_mitigated > 0 and current_alert < config.SYSTEM["MAX_ALERT_LEVEL"]:
                     self.state_manager.update_war_state({'blue_alert_level': min(config.SYSTEM["MAX_ALERT_LEVEL"], current_alert + 1)})

                if self.running:
                    self.sync_memory()
                    time.sleep(random.uniform(0.5, 1.5))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"SOC Loop Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    BlueDefender().engage()
