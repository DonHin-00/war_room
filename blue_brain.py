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
import json
from typing import Dict, Any, List, Deque, Set

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
    def __init__(self):
        self.alpha = config.RL["ALPHA"]
        self.alpha_decay = config.RL["ALPHA_DECAY"]
        self.gamma = config.RL["GAMMA"]
        self.epsilon = config.RL["EPSILON_START"]
        self.epsilon_decay = config.RL["EPSILON_DECAY"]

        self.q_table: Dict[str, float] = {}
        self.running = True
        self.state_manager = utils.StateManager(config.PATHS["WAR_STATE"])
        self.signature_db = SignatureDatabase(config.PATHS["SIGNATURES"])
        self.audit_logger = utils.AuditLogger(config.PATHS["AUDIT_LOG"])

        self.threat_history: Deque[int] = collections.deque(maxlen=config.BLUE["THRESHOLDS"]["ANOMALY_WINDOW"])
        self.traps_deployed = False

        # Backup system
        self.backups: Dict[str, bytes] = {}

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def load_memory(self):
        self.q_table = self.state_manager.load_json(config.PATHS["Q_TABLE_BLUE"])
        logger.info(f"Memory Loaded. Q-Table Size: {len(self.q_table)}")

    def sync_memory(self):
        self.state_manager.save_json(config.PATHS["Q_TABLE_BLUE"], self.q_table)

    def shutdown(self, signum, frame):
        logger.info("Shutting down... Syncing memory.")
        self.sync_memory()
        self.running = False
        sys.exit(0)

    def detect_anomaly(self, current_threat_count: int) -> bool:
        self.threat_history.append(current_threat_count)
        if len(self.threat_history) < 3: return False
        avg = sum(self.threat_history) / len(self.threat_history)
        return current_threat_count > avg * 2 and current_threat_count > 2

    def deploy_nasty_defenses(self):
        if not os.path.exists(config.PATHS["WAR_ZONE"]): return
        utils.create_tar_pit(os.path.join(config.PATHS["WAR_ZONE"], "access.log"))
        utils.create_logic_bomb(os.path.join(config.PATHS["WAR_ZONE"], "shadow_backup"))
        self.traps_deployed = True
        logger.info("NASTY DEFENSES DEPLOYED.")

    def perform_backup(self):
        """Simulates backing up 'critical' files."""
        # For simulation, we just store content of some files in memory or a backup dir.
        # Let's say we backup random safe files.
        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file() and not entry.name.endswith(".enc") and not utils.is_tar_pit(entry.path):
                        # Backup logic
                        try:
                            content = utils.safe_file_read(entry.path)
                            self.backups[entry.name] = content
                        except: pass
            return 1
        except: return 0

    def restore_data(self):
        """Restores files if they are missing or encrypted."""
        restored = 0
        for fname, content in self.backups.items():
            fpath = os.path.join(config.PATHS["WAR_ZONE"], fname)
            enc_path = fpath + ".enc"

            # Check if encrypted version exists or original missing
            if os.path.exists(enc_path):
                os.remove(enc_path)
                with open(fpath, 'w') as f: f.write(content) # Not binary safe in backup dict? assuming str
                restored += 1
            elif not os.path.exists(fpath):
                with open(fpath, 'w') as f: f.write(content)
                restored += 1
        return restored

    def generate_incident_report(self, threat_type, threat_path):
        """Generates a JSON incident report."""
        report = {
            "timestamp": time.time(),
            "type": threat_type,
            "path": threat_path,
            "action": "MITIGATED",
            "signature": "HEURISTIC_MATCH"
        }
        fname = f"ir_{int(time.time())}_{random.randint(1000,9999)}.json"
        utils.safe_json_write(os.path.join(config.PATHS["INCIDENTS"], fname), report)

    def engage(self):
        logger.info("Blue Team AI Initialized. Policy: NIST SP 800-61 + Adaptive Immunity")
        self.load_memory()

        while self.running:
            try:
                # 1. PREPARATION
                war_state = self.state_manager.get_war_state()
                if not war_state: war_state = {'blue_alert_level': 1}
                current_alert = war_state.get('blue_alert_level', 1)

                # 2. DETECTION
                if not os.path.exists(config.PATHS["WAR_ZONE"]):
                    os.makedirs(config.PATHS["WAR_ZONE"], exist_ok=True)

                visible_threats = []
                all_threats = []
                encrypted_files = []
                c2_beacons = []

                with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                    for entry in it:
                        if utils.is_tar_pit(entry.path) or utils.is_honeypot(entry.path):
                            continue
                        if entry.is_file():
                            path = entry.path
                            if path.endswith(".enc"):
                                encrypted_files.append(path)
                            elif "c2_beacon" in entry.name:
                                c2_beacons.append(path)
                            else:
                                all_threats.append(path)
                                if "malware" in entry.name:
                                    visible_threats.append(path)

                threat_count = len(all_threats) + len(encrypted_files)

                anomaly_detected = self.detect_anomaly(threat_count)
                if anomaly_detected and current_alert < config.SYSTEM["MAX_ALERT_LEVEL"]:
                    self.state_manager.update_war_state({'blue_alert_level': min(config.SYSTEM["MAX_ALERT_LEVEL"], current_alert + 1)})

                state_key = f"{current_alert}_{threat_count}"

                # 3. DECISION
                if random.random() < self.epsilon:
                    action = random.choice(config.BLUE["ACTIONS"])
                else:
                    best_action = None
                    max_q = -float('inf')
                    for a in config.BLUE["ACTIONS"]:
                        q = self.q_table.get(f"{state_key}_{a}", 0.0)
                        if q > max_q:
                            max_q = q
                            best_action = a
                    action = best_action if best_action else random.choice(config.BLUE["ACTIONS"])

                self.epsilon = max(config.RL["EPSILON_MIN"], self.epsilon * self.epsilon_decay)
                self.alpha = max(0.1, self.alpha * self.alpha_decay)

                # 4. EXECUTION
                mitigated = 0
                details = {}

                if action == "DEPLOY_TRAP" or action == "DEPLOY_DECOY":
                    if not self.traps_deployed:
                        self.deploy_nasty_defenses()
                        details = {"defense": "traps_deployed"}

                elif action == "BACKUP_CRITICAL":
                    count = self.perform_backup()
                    details = {"action": "backup", "count": count}

                elif action == "RESTORE_DATA":
                    if encrypted_files:
                        count = self.restore_data()
                        if count > 0:
                            mitigated += 2
                            details = {"action": "restore", "count": count}

                elif action == "SIGNATURE_SCAN":
                    for t in all_threats + c2_beacons:
                        try:
                            data = utils.safe_file_read(t, timeout=0.1)
                            # Simple C2 signature check or hash check
                            if self.signature_db.check_signature(data) or "HEARTBEAT" in str(data):
                                os.remove(t)
                                mitigated += 1
                                self.generate_incident_report("KNOWN_THREAT", t)
                        except: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        try:
                            data = utils.safe_file_read(t, timeout=0.1)
                            entropy = utils.calculate_entropy(data)

                            if ".sys" in t or entropy > config.BLUE["THRESHOLDS"]["ENTROPY"]:
                                os.remove(t)
                                mitigated += 1
                                self.signature_db.add_signature(data)
                                self.generate_incident_report("HEURISTIC_THREAT", t)
                        except: pass

                # 5. REWARDS
                reward = 0
                if mitigated > 0: reward = config.BLUE["REWARDS"]["MITIGATION"]
                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = config.BLUE["REWARDS"]["PENALTY_WASTE"]
                if current_alert >= 4 and action == "OBSERVE": reward = config.BLUE["REWARDS"]["PATIENCE"]
                if action == "IGNORE" and threat_count > 0: reward = config.BLUE["REWARDS"]["PENALTY_NEGLIGENCE"]
                if anomaly_detected and action == "HEURISTIC_SCAN": reward += config.BLUE["REWARDS"]["ANOMALY_BONUS"]
                if action == "RESTORE_DATA" and mitigated > 0: reward += config.BLUE["REWARDS"]["RESTORE_SUCCESS"]

                # 6. LEARN
                current_q_key = f"{state_key}_{action}"
                old_val = self.q_table.get(current_q_key, 0.0)
                next_max = -float('inf')
                for a in config.BLUE["ACTIONS"]:
                    q = self.q_table.get(f"{state_key}_{a}", 0.0)
                    if q > next_max: next_max = q
                if next_max == -float('inf'): next_max = 0.0

                new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
                self.q_table[current_q_key] = new_val

                self.sync_memory()

                # 7. OPS LOGGING
                self.audit_logger.log_event("BLUE", action, {
                    "mitigated": mitigated,
                    "alert_level": current_alert,
                    **details
                })

                # 8. UPDATE WAR STATE
                if mitigated > 0 and current_alert < config.SYSTEM["MAX_ALERT_LEVEL"]:
                    self.state_manager.update_war_state({'blue_alert_level': min(config.SYSTEM["MAX_ALERT_LEVEL"], current_alert + 1)})
                elif mitigated == 0 and current_alert > config.SYSTEM["MIN_ALERT_LEVEL"] and action == "OBSERVE":
                    self.state_manager.update_war_state({'blue_alert_level': max(config.SYSTEM["MIN_ALERT_LEVEL"], current_alert - 1)})

                icon = "🛡️" if mitigated == 0 else "⚔️"
                logger.info(f"{icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")

                time.sleep(random.uniform(0.1, 0.5))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    BlueDefender().engage()
