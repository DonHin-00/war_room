#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import random
import signal
import sys
import logging
import secrets
import shutil
from typing import Dict, Any, Optional

import utils
import config

# Setup Logging
utils.setup_logging(config.PATHS["LOG_RED"])
logger = logging.getLogger("RedTeam")

class RedTeamer:
    """
    The Red Team AI Agent with Double Q-Learning, Experience Replay, and Advanced Tactics.
    """
    def __init__(self):
        self.alpha = config.RL["ALPHA"]
        self.alpha_decay = config.RL["ALPHA_DECAY"]
        self.gamma = config.RL["GAMMA"]
        self.epsilon = config.RL["EPSILON_START"]
        self.epsilon_decay = config.RL["EPSILON_DECAY"]

        self.q_tables: Dict[str, Dict[str, float]] = {"A": {}, "B": {}}
        self.replay_buffer = utils.ExperienceReplay(capacity=config.RL["MEMORY_CAPACITY"])
        self.audit_logger = utils.AuditLogger(config.PATHS["AUDIT_LOG"])

        self.running = True
        self.iteration_count = 0

        self.state_manager = utils.StateManager(config.PATHS["WAR_STATE"])

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def load_memory(self):
        data = self.state_manager.load_json(config.PATHS["Q_TABLE_RED"])
        if "A" in data and "B" in data:
            self.q_tables = data
        else:
            self.q_tables["A"] = data
            self.q_tables["B"] = {}
        logger.info(f"Memory Loaded. Q-Table A Size: {len(self.q_tables['A'])}")

    def sync_memory(self):
        self.state_manager.save_json(config.PATHS["Q_TABLE_RED"], self.q_tables)

    def shutdown(self, signum, frame):
        logger.info("Shutting down... Syncing memory.")
        self.sync_memory()
        self.running = False
        sys.exit(0)

    def get_q_value(self, state_key, action):
        qa = self.q_tables["A"].get(f"{state_key}_{action}", 0.0)
        qb = self.q_tables["B"].get(f"{state_key}_{action}", 0.0)
        return (qa + qb) / 2.0

    def learn(self):
        if len(self.replay_buffer) < config.RL["BATCH_SIZE"]: return

        batch = self.replay_buffer.sample(config.RL["BATCH_SIZE"])

        for state, action, reward, next_state in batch:
            if random.random() < 0.5:
                update_a = True
                main_table = self.q_tables["A"]
                target_table = self.q_tables["B"]
            else:
                update_a = False
                main_table = self.q_tables["B"]
                target_table = self.q_tables["A"]

            max_next_q = -float('inf')
            best_next_action = None
            for a in config.RED["ACTIONS"]:
                q = main_table.get(f"{next_state}_{a}", 0.0)
                if q > max_next_q:
                    max_next_q = q
                    best_next_action = a
            if best_next_action is None: best_next_action = random.choice(config.RED["ACTIONS"])

            target_value = target_table.get(f"{next_state}_{best_next_action}", 0.0)

            current_q_key = f"{state}_{action}"
            old_val = main_table.get(current_q_key, 0.0)

            new_val = old_val + self.alpha * (reward + self.gamma * target_value - old_val)
            main_table[current_q_key] = new_val

    def perform_recon(self):
        """Safely inspects the environment to find targets or traps."""
        traps_found = 0
        try:
            if not os.path.exists(config.PATHS["WAR_ZONE"]): return 0
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if utils.is_tar_pit(entry.path):
                        traps_found += 1
                        continue
                    if entry.is_file():
                        if utils.is_honeypot(entry.path):
                             traps_found += 1
        except OSError: pass
        return traps_found

    def generate_payload(self, obfuscate=False):
        """Generates payload content. Obfuscation adds random high-entropy padding."""
        base_content = b"echo 'malware_payload'"
        if obfuscate:
            # Polymorphism: Different padding every time
            padding = utils.generate_high_entropy_data(random.randint(512, 4096))
            return base_content + b"\n#PAD:" + padding
        return base_content

    def encrypt_target(self):
        """Simulates Ransomware: Find a file and rename/encrypt it."""
        try:
            if not os.path.exists(config.PATHS["WAR_ZONE"]): return 0
            targets = []
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file() and not entry.name.endswith(".enc") and not utils.is_tar_pit(entry.path):
                        targets.append(entry.path)

            if not targets: return 0

            target = random.choice(targets)
            # Read content (safe read)
            content = utils.safe_file_read(target)
            if not content: return 0

            # Simulate encryption (Base64 or simple reversal for simulation)
            # We just append .enc and overwrite with "ENCRYPTED" header
            encrypted_path = target + ".enc"
            with open(encrypted_path, 'wb') as f:
                f.write(b"ENCRYPTED_HEADER_V1")
                f.write(utils.generate_high_entropy_data(128))

            os.remove(target)
            return 1
        except Exception:
            return 0

    def engage(self):
        logger.info("Red Team AI Initialized. Framework: MITRE ATT&CK + Polymorphism")
        self.load_memory()

        if not os.path.exists(config.PATHS["WAR_ZONE"]):
            os.makedirs(config.PATHS["WAR_ZONE"], exist_ok=True)

        while self.running:
            try:
                self.iteration_count += 1
                
                # 1. RECON
                war_state = self.state_manager.get_war_state()
                if not war_state: war_state = {'blue_alert_level': 1}
                current_alert = war_state.get('blue_alert_level', 1)

                # Check for last attack success (Feedback Loop)
                # Ideally check if file still exists. Simplified here.

                sync_interval = config.RL["SYNC_INTERVAL"] * current_alert
                state_key = f"{current_alert}"

                # 2. STRATEGY
                if random.random() < self.epsilon:
                    action = random.choice(config.RED["ACTIONS"])
                else:
                    best_action = None
                    max_q = -float('inf')
                    for a in config.RED["ACTIONS"]:
                        q = self.get_q_value(state_key, a)
                        if q > max_q:
                            max_q = q
                            best_action = a
                    action = best_action if best_action else random.choice(config.RED["ACTIONS"])

                self.epsilon = max(config.RL["EPSILON_MIN"], self.epsilon * self.epsilon_decay)
                self.alpha = max(0.1, self.alpha * self.alpha_decay)

                # 3. EXECUTION
                impact = 0
                trapped = False
                details = {}

                try:
                    rand_suffix = secrets.token_hex(4)
                    timestamp = int(time.time())
                    target_file = None

                    if action == "T1046_RECON":
                        self.perform_recon()
                        impact = 1
                        details = {"type": "recon"}

                    elif action == "T1027_OBFUSCATE":
                        fname = f"malware_crypt_{timestamp}_{rand_suffix}.bin"
                        target_file = os.path.join(config.PATHS["WAR_ZONE"], fname)
                        with open(target_file, 'wb') as f:
                            f.write(self.generate_payload(obfuscate=True))
                        impact = 3
                        details = {"file": fname, "technique": "obfuscation"}

                    elif action == "T1003_ROOTKIT":
                        fname = f".sys_shadow_{timestamp}_{rand_suffix}"
                        target_file = os.path.join(config.PATHS["WAR_ZONE"], fname)
                        with open(target_file, 'w') as f: f.write("uid=0(root)")
                        impact = 5
                        details = {"file": fname, "technique": "rootkit"}

                    elif action == "T1036_MASQUERADE":
                        names = ["system.log", "config.ini", "update.tmp"]
                        fname = f"{random.choice(names)}_{rand_suffix}"
                        target_file = os.path.join(config.PATHS["WAR_ZONE"], fname)
                        with open(target_file, 'w') as f: f.write(" benign_looking_header=1\n")
                        with open(target_file, 'ab') as f:
                            f.write(self.generate_payload(obfuscate=True))
                        impact = 4
                        details = {"file": fname, "technique": "masquerade"}

                    elif action == "T1486_ENCRYPT":
                        success = self.encrypt_target()
                        if success:
                            impact = 8
                            details = {"technique": "ransomware", "status": "encrypted"}
                        else:
                            impact = 0

                    elif action == "T1071_C2_BEACON":
                        # Create a persistent beacon file or update it
                        fname = "c2_beacon.dat"
                        target_file = os.path.join(config.PATHS["WAR_ZONE"], fname)
                        with open(target_file, 'a') as f:
                            f.write(f"{timestamp}:HEARTBEAT\n")
                        impact = 2
                        details = {"file": fname, "technique": "c2"}

                    elif action == "T1589_LURK":
                        impact = 0
                        details = {"technique": "lurk"}

                except OSError as e:
                    trapped = True
                    logger.warning(f"Attack thwarted: {e}")
                    details["error"] = str(e)

                # 4. REWARDS
                reward = 0
                if impact > 0: reward = config.RED["REWARDS"]["IMPACT"]
                if current_alert >= 4 and action == "T1589_LURK": reward = config.RED["REWARDS"]["STEALTH"]
                if current_alert == config.SYSTEM["MAX_ALERT_LEVEL"] and impact > 0: reward = config.RED["REWARDS"]["CRITICAL"]
                if trapped: reward = config.RED["REWARDS"]["PENALTY_TRAPPED"]

                # 5. LEARN
                self.replay_buffer.push(state_key, action, reward, state_key)
                self.learn()

                if self.iteration_count % sync_interval == 0:
                    self.sync_memory()

                # 6. OPS LOGGING
                self.audit_logger.log_event("RED", action, {
                    "impact": impact,
                    "alert_level": current_alert,
                    **details
                })

                # 7. TRIGGER ALERTS
                if impact > 0 and random.random() > 0.5:
                    new_level = min(config.SYSTEM["MAX_ALERT_LEVEL"], current_alert + 1)
                    if new_level != current_alert:
                         self.state_manager.update_war_state({'blue_alert_level': new_level})

                logger.info(f"State: {state_key} | Tech: {action} | Impact: {impact} | Q(avg): {self.get_q_value(state_key, action):.2f}")
                time.sleep(random.uniform(0.1, 0.5))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    RedTeamer().engage()
