#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import json
import random
import uuid
import signal
import sys
import logging
from utils import safe_file_read, safe_file_write

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
LOG_FILE = os.path.join(BASE_DIR, "red.log")
TARGET_DIR = "/tmp"

# --- HYPERPARAMETERS ---
ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK", "T1036_MASQUERADE", "T1486_ENCRYPT"]
ALPHA = 0.4
ALPHA_DECAY = 0.9999
GAMMA = 0.9
EPSILON = 0.3
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01

# --- REWARDS ---
R_IMPACT = 10
R_STEALTH = 15
R_CRITICAL = 30
MAX_ALERT = 5

class RedAttacker:
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
        self.logger = logging.getLogger("RedTeam")

    def handle_signal(self, signum, frame):
        self.logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.running = False

    def load_state(self):
        self.q_table = self._access_memory(Q_TABLE_FILE)
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

    def run(self):
        self.logger.info("Red Team AI Initialized. APT Framework: ACTIVE")

        while self.running:
            try:
                # 1. RECON
                self.war_state = self._access_memory(STATE_FILE) or {'blue_alert_level': 1}
                current_alert = self.war_state.get('blue_alert_level', 1)
                state_key = f"{current_alert}"

                # 2. STRATEGY
                if random.random() < self.epsilon:
                    action = random.choice(ACTIONS)
                else:
                    known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                    action = max(known, key=known.get)
                
                self.epsilon = max(MIN_EPSILON, self.epsilon * EPSILON_DECAY)
                self.alpha = max(0.1, self.alpha * ALPHA_DECAY)

                # 3. EXECUTION
                impact = 0

                if action == "T1046_RECON":
                    fname = os.path.join(TARGET_DIR, f"malware_bait_{uuid.uuid4()}.sh")
                    try:
                        fd = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                        with os.fdopen(fd, 'w') as f: f.write("echo 'scan'")
                        impact = 1
                    except OSError: pass

                elif action == "T1027_OBFUSCATE":
                    fname = os.path.join(TARGET_DIR, f"malware_crypt_{uuid.uuid4()}.bin")
                    try:
                        fd = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                        with os.fdopen(fd, 'wb') as f:
                            payload = b"\x90" * 100 + b"\xcc" * 50
                            padding = os.urandom(random.randint(1, 100))
                            f.write(payload + padding)
                        impact = 3
                    except OSError: pass

                elif action == "T1003_ROOTKIT":
                    fname = os.path.join(TARGET_DIR, f".sys_shadow_{uuid.uuid4()}")
                    try:
                        fd = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                        with os.fdopen(fd, 'w') as f: f.write("uid=0(root)")
                        impact = 5
                    except OSError: pass

                elif action == "T1589_LURK":
                    impact = 0

                elif action == "T1036_MASQUERADE":
                    fname = os.path.join(TARGET_DIR, f"system_log_{uuid.uuid4()}.txt")
                    try:
                        fd = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                        with os.fdopen(fd, 'wb') as f:
                            f.write(b"\xde\xad\xbe\xef" * 100 + os.urandom(100))
                        with open(fname, 'wb') as f:
                            f.write(b"StaticMaliciousPayload" * 50 + b"\x00\xff" * 50)
                        impact = 2
                    except OSError: pass

                elif action == "T1486_ENCRYPT":
                    try:
                        targets = []
                        with os.scandir(TARGET_DIR) as entries:
                            for entry in entries:
                                if entry.is_file() and not entry.name.startswith(("malware_", ".sys_", "RANSOM_")):
                                    if not entry.name.endswith(".enc"):
                                        targets.append(entry.path)
                        if targets:
                            target = random.choice(targets)
                            new_name = target + ".enc"
                            with open(target, 'rb') as f_in: data = f_in.read()
                            encrypted_data = bytearray([b ^ 0x42 for b in data])
                            fd = os.open(new_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                            with os.fdopen(fd, 'wb') as f_out: f_out.write(encrypted_data)
                            os.remove(target)

                            note = os.path.join(TARGET_DIR, f"RANSOM_NOTE_{uuid.uuid4()}.txt")
                            with open(note, 'w') as f: f.write("YOUR FILES ARE ENCRYPTED. PAY 1 BTC.")
                            impact = 5
                    except Exception: pass

                # 4. REWARDS
                reward = 0
                if impact > 0: reward = R_IMPACT
                if current_alert >= 4 and action == "T1589_LURK": reward = R_STEALTH
                if current_alert == MAX_ALERT and impact > 0: reward = R_CRITICAL

                # 5. LEARN
                old_val = self.q_table.get(f"{state_key}_{action}", 0)
                next_max = max([self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + self.alpha * (reward + GAMMA * next_max - old_val)
                self.q_table[f"{state_key}_{action}"] = new_val
                self._access_memory(Q_TABLE_FILE, self.q_table)

                # 6. TRIGGER ALERTS
                if impact > 0 and random.random() > 0.5:
                    self.war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 1)
                    self._access_memory(STATE_FILE, self.war_state)

                # LOG
                self.logger.info(f"👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")

                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                self.logger.error(f"Main loop error: {e}")
                time.sleep(1)

        self.logger.info("Red Team AI Shutdown.")

if __name__ == "__main__":
    attacker = RedAttacker()
    attacker.run()
