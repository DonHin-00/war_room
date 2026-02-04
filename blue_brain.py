#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield
"""

import os
import time
import json
import random
import math
import hashlib
import shutil
import signal
import sys
import logging
from utils import safe_file_read, safe_file_write

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "blue_q_table.json")
SIGNATURES_FILE = os.path.join(BASE_DIR, "signatures.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
LOG_FILE = os.path.join(BASE_DIR, "blue.log")
WATCH_DIR = "/tmp"
BACKUP_DIR = os.path.join(WATCH_DIR, ".blue_backups")

# Ensure Directories
if not os.path.exists(BACKUP_DIR):
    try: os.mkdir(BACKUP_DIR)
    except OSError: pass

# --- HYPERPARAMETERS ---
ACTIONS = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "DEPLOY_DECOY", "BACKUP_RESTORE", "OBSERVE", "IGNORE"]
ALPHA = 0.4
ALPHA_DECAY = 0.9999
GAMMA = 0.9
EPSILON = 0.3
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01

# --- REWARDS ---
R_MITIGATION = 25
R_PATIENCE = 10
P_WASTE = -15
P_NEGLIGENCE = -50
MAX_ALERT = 5
MIN_ALERT = 1

class BlueDefender:
    def __init__(self):
        self.running = True
        self.epsilon = EPSILON
        self.alpha = ALPHA
        self.setup_logging()
        self.load_state()

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
        self.logger = logging.getLogger("BlueTeam")

    def handle_signal(self, signum, frame):
        self.logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False

    def load_state(self):
        self.q_table = self._access_memory(Q_TABLE_FILE)
        self.signatures = self._access_memory(SIGNATURES_FILE)
        if not isinstance(self.signatures, list): self.signatures = []
        self.war_state = self._access_memory(STATE_FILE)
        if not self.war_state: self.war_state = {'blue_alert_level': 1}

    def _access_memory(self, filepath, data=None):
        if data is not None:
            try:
                safe_file_write(filepath, json.dumps(data, indent=4))
            except Exception as e:
                self.logger.error(f"Failed to write to {filepath}: {e}")

        if os.path.exists(filepath):
            try:
                content = safe_file_read(filepath)
                return json.loads(content) if content else {}
            except Exception as e:
                self.logger.error(f"Failed to read from {filepath}: {e}")
                return {}
        return {}

    def calculate_shannon_entropy(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                data = f.read(4096)
                if not data: return 0
                entropy = 0
                for x in range(256):
                    p_x = float(data.count(x.to_bytes(1, 'little'))) / len(data)
                    if p_x > 0:
                        entropy += - p_x * math.log(p_x, 2)
                return entropy
        except Exception:
            return 0

    def calculate_hash(self, filepath):
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while True:
                    data = f.read(65536)
                    if not data: break
                    sha256.update(data)
            return sha256.hexdigest()
        except Exception:
            return None

    def scan_directory(self):
        visible_threats = []
        hidden_threats = []
        all_files = []
        try:
            with os.scandir(WATCH_DIR) as entries:
                for entry in entries:
                    all_files.append(entry.path)
                    if entry.name.startswith('malware_'):
                        visible_threats.append(entry.path)
                    elif entry.name.startswith('.sys_'):
                        hidden_threats.append(entry.path)
        except OSError as e:
            self.logger.error(f"Scan error: {e}")
        return visible_threats, hidden_threats, all_files

    def run(self):
        self.logger.info("Blue Team AI Initialized. Policy: NIST SP 800-61")

        while self.running:
            try:
                # 1. PREPARATION
                self.war_state = self._access_memory(STATE_FILE) or {'blue_alert_level': 1}
                current_alert = self.war_state.get('blue_alert_level', 1)

                # 2. DETECTION
                visible_threats, hidden_threats, all_files = self.scan_directory()
                all_threats = visible_threats + hidden_threats
                threat_count = len(all_threats)
                state_key = f"{current_alert}_{threat_count}"

                # 3. DECISION
                if random.random() < self.epsilon:
                    action = random.choice(ACTIONS)
                else:
                    known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                    action = max(known, key=known.get)

                self.epsilon = max(MIN_EPSILON, self.epsilon * EPSILON_DECAY)
                self.alpha = max(0.1, self.alpha * ALPHA_DECAY)

                # 4. ERADICATION / ACTION
                mitigated = 0

                if action == "SIGNATURE_SCAN":
                    targets = set(visible_threats)
                    for f in all_files:
                        if self.calculate_hash(f) in self.signatures:
                            targets.add(f)
                    for t in targets:
                        try:
                            if not os.path.islink(t):
                                os.remove(t)
                                mitigated += 1
                        except OSError: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        if ".sys" in t or self.calculate_shannon_entropy(t) > 3.5:
                            try:
                                if not os.path.islink(t):
                                    f_hash = self.calculate_hash(t)
                                    if f_hash and f_hash not in self.signatures:
                                        self.signatures.append(f_hash)
                                        self._access_memory(SIGNATURES_FILE, self.signatures)
                                    os.remove(t)
                                    mitigated += 1
                            except OSError: pass

                elif action == "DEPLOY_DECOY":
                    decoys = ["passwords.txt", "config.yaml", "aws_keys.csv"]
                    for d in decoys:
                        fname = os.path.join(WATCH_DIR, d)
                        if not os.path.exists(fname):
                            try: safe_file_write(fname, "HONEYPOT_TOKEN_DO_NOT_TOUCH")
                            except Exception: pass

                elif action == "BACKUP_RESTORE":
                    # Backup
                    try:
                        with os.scandir(WATCH_DIR) as entries:
                            for entry in entries:
                                if entry.is_file() and entry.name.endswith((".txt", ".yaml", ".csv")) and not entry.name.startswith("RANSOM"):
                                    shutil.copy2(entry.path, os.path.join(BACKUP_DIR, entry.name))
                    except OSError: pass

                    # Restore
                    try:
                        with os.scandir(WATCH_DIR) as entries:
                            for entry in entries:
                                if entry.name.endswith(".enc"):
                                    original_name = entry.name[:-4]
                                    backup_path = os.path.join(BACKUP_DIR, original_name)
                                    try: os.remove(entry.path)
                                    except OSError: pass
                                    if os.path.exists(backup_path):
                                        shutil.copy2(backup_path, os.path.join(WATCH_DIR, original_name))
                                        mitigated += 1
                                elif entry.name.startswith("RANSOM_NOTE"):
                                    try: os.remove(entry.path)
                                    except OSError: pass
                    except OSError: pass

                # 5. REWARD
                reward = 0
                if mitigated > 0: reward = R_MITIGATION
                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = P_WASTE
                if current_alert >= 4 and action == "OBSERVE": reward = R_PATIENCE
                if action == "IGNORE" and threat_count > 0: reward = P_NEGLIGENCE

                # 6. LEARN
                old_val = self.q_table.get(f"{state_key}_{action}", 0)
                next_max = max([self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + self.alpha * (reward + GAMMA * next_max - old_val)
                self.q_table[f"{state_key}_{action}"] = new_val
                
                # Sync logic could be improved to not write every frame, but keeping it simple for now
                self._access_memory(Q_TABLE_FILE, self.q_table)

                # 7. UPDATE WAR STATE
                if mitigated > 0 and current_alert < MAX_ALERT:
                    self.war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 1)
                elif mitigated == 0 and current_alert > MIN_ALERT and action == "OBSERVE":
                    self.war_state['blue_alert_level'] = max(MIN_ALERT, current_alert - 1)
                self._access_memory(STATE_FILE, self.war_state)

                # LOG
                icon = "🛡️" if mitigated == 0 else "⚔️"
                self.logger.info(f"{icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")

                time.sleep(0.5 if current_alert >= 4 else 1.0)

            except Exception as e:
                self.logger.error(f"Main loop error: {e}")
                time.sleep(1)

        self.logger.info("Blue Team AI Shutdown.")

if __name__ == "__main__":
    defender = BlueDefender()
    defender.run()
