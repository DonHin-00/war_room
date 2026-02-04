#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix

This module implements the Red Team AI, an automated adversary that simulates
APT (Advanced Persistent Threat) behaviors. It uses Double Q-Learning and
Experience Replay to adapt its strategy based on the defensive posture.
"""

import os
import time
import random
import signal
import sys
import logging
import secrets
from typing import Dict, Any, Optional

import utils

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
TARGET_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK"]
MIN_EPSILON = 0.01
BATCH_SIZE = 8          # Mini-batch size for Experience Replay

# --- REWARD CONFIGURATION (ATTACKER PROFILE) ---
R_IMPACT = 10           # Base points for successful drop
R_STEALTH = 15          # Points for lurking when heat is high
R_CRITICAL = 30         # Bonus for attacking during Max Alert (Brazen)
P_TRAPPED = -20         # Penalty for falling into a trap
MAX_ALERT = 5

# --- PERFORMANCE CONFIGURATION ---
BASE_SYNC_INTERVAL = 10      # Base sync interval

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format=f"{C_RED}[%(levelname)s] %(message)s{C_RESET}"
)
logger = logging.getLogger("RedTeam")

# --- UTILITIES ---

class StateManager:
    """
    Manages state persistence with caching and optimization.
    Uses utils.py for safe file operations.
    """
    def __init__(self):
        self.state_cache: Dict[str, Any] = {}
        self.state_mtime: float = 0.0

    def load_json(self, filepath: str) -> Dict[str, Any]:
        """Safely loads JSON data from a file."""
        return utils.safe_json_read(filepath)

    def save_json(self, filepath: str, data: Dict[str, Any]) -> None:
        """Safely saves JSON data to a file using atomic write patterns."""
        utils.safe_json_write(filepath, data)

    def get_war_state(self) -> Dict[str, Any]:
        """
        Retrieves the shared war state.
        Optimized to only read from disk if the file has been modified.
        """
        if not os.path.exists(STATE_FILE):
            return {'blue_alert_level': 1}

        try:
            mtime = os.stat(STATE_FILE).st_mtime
            if mtime > self.state_mtime:
                self.state_cache = self.load_json(STATE_FILE)
                self.state_mtime = mtime
        except OSError:
            pass

        return self.state_cache

    def update_war_state(self, updates: Dict[str, Any]) -> None:
        """Updates the shared war state."""
        current = self.load_json(STATE_FILE)
        current.update(updates)
        self.save_json(STATE_FILE, current)
        self.state_cache = current
        try:
            self.state_mtime = os.stat(STATE_FILE).st_mtime
        except OSError:
            self.state_mtime = time.time()


class RedTeamer:
    """
    The Red Team AI Agent with Double Q-Learning and Experience Replay.
    """
    def __init__(self):
        self.alpha = 0.4
        self.alpha_decay = 0.9999
        self.gamma = 0.9
        self.epsilon = 0.3
        self.epsilon_decay = 0.995

        self.q_tables: Dict[str, Dict[str, float]] = {"A": {}, "B": {}}
        self.replay_buffer = utils.ExperienceReplay(capacity=1000)

        self.running = True
        self.iteration_count = 0

        self.state_manager = StateManager()

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def load_memory(self):
        data = self.state_manager.load_json(Q_TABLE_FILE)
        if "A" in data and "B" in data:
            self.q_tables = data
        else:
            self.q_tables["A"] = data
            self.q_tables["B"] = {}
        logger.info(f"Memory Loaded. Q-Table A Size: {len(self.q_tables['A'])}, B Size: {len(self.q_tables['B'])}")

    def sync_memory(self):
        self.state_manager.save_json(Q_TABLE_FILE, self.q_tables)

    def shutdown(self, signum, frame):
        logger.info("Shutting down... Syncing memory.")
        self.sync_memory()
        self.running = False
        sys.exit(0)

    def get_q_value(self, state_key, action):
        """Returns the average Q value from both tables."""
        qa = self.q_tables["A"].get(f"{state_key}_{action}", 0.0)
        qb = self.q_tables["B"].get(f"{state_key}_{action}", 0.0)
        return (qa + qb) / 2.0

    def learn(self):
        """Perform Double Q-Learning update using a batch from replay buffer."""
        if len(self.replay_buffer) < BATCH_SIZE:
            return

        batch = self.replay_buffer.sample(BATCH_SIZE)

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
            for a in ACTIONS:
                q = main_table.get(f"{next_state}_{a}", 0.0)
                if q > max_next_q:
                    max_next_q = q
                    best_next_action = a
            if best_next_action is None: best_next_action = random.choice(ACTIONS)

            target_value = target_table.get(f"{next_state}_{best_next_action}", 0.0)

            current_q_key = f"{state}_{action}"
            old_val = main_table.get(current_q_key, 0.0)

            new_val = old_val + self.alpha * (reward + self.gamma * target_value - old_val)
            main_table[current_q_key] = new_val

    def perform_recon(self):
        """
        Safely inspects the environment to find targets or traps.
        """
        traps_found = 0
        try:
            # We only look at TARGET_DIR if it exists
            if not os.path.exists(TARGET_DIR): return 0

            # Use os.scandir for speed and to check attributes without opening
            with os.scandir(TARGET_DIR) as it:
                for entry in it:
                    # entry.is_file() returns False for FIFOs/Pipes!
                    # We must check if it's a pipe specifically or just use is_tar_pit on path
                    if utils.is_tar_pit(entry.path):
                        traps_found += 1
                        continue # Don't touch it!

                    if entry.is_file():
                        # Check for Honeypots (Obfuscated check)
                        if utils.is_honeypot(entry.path):
                             traps_found += 1
                             continue

                        # Try to read safe files to 'learn' system structure?
                        # This simulates learning environment.
        except OSError:
            pass
        return traps_found

    def engage(self):
        logger.info("Red Team AI Initialized. Framework: Double Q-Learning + Replay")
        self.load_memory()

        if not os.path.exists(TARGET_DIR):
            try: os.makedirs(TARGET_DIR)
            except OSError: pass

        while self.running:
            try:
                self.iteration_count += 1
                
                # 1. RECON
                war_state = self.state_manager.get_war_state()
                if not war_state: war_state = {'blue_alert_level': 1}
                current_alert = war_state.get('blue_alert_level', 1)

                sync_interval = BASE_SYNC_INTERVAL * current_alert
                state_key = f"{current_alert}"

                # 2. STRATEGY
                if random.random() < self.epsilon:
                    action = random.choice(ACTIONS)
                else:
                    best_action = None
                    max_q = -float('inf')
                    for a in ACTIONS:
                        q = self.get_q_value(state_key, a)
                        if q > max_q:
                            max_q = q
                            best_action = a
                    action = best_action if best_action else random.choice(ACTIONS)

                self.epsilon = max(MIN_EPSILON, self.epsilon * self.epsilon_decay)
                self.alpha = max(0.1, self.alpha * self.alpha_decay)

                # 3. EXECUTION
                impact = 0
                trapped = False

                try:
                    rand_suffix = secrets.token_hex(4)
                    timestamp = int(time.time())

                    if action == "T1046_RECON":
                        # Updated Recon: Actually look around, risk traps
                        traps_avoided = self.perform_recon()
                        # If we found traps, we 'succeeded' in recon but impact is info, not damage.
                        fname = os.path.join(TARGET_DIR, f"malware_bait_{timestamp}_{rand_suffix}.sh")
                        with open(fname, 'w') as f: f.write("echo 'scan'")
                        impact = 1

                    elif action == "T1027_OBFUSCATE":
                        fname = os.path.join(TARGET_DIR, f"malware_crypt_{timestamp}_{rand_suffix}.bin")
                        with open(fname, 'wb') as f: f.write(utils.generate_high_entropy_data(1024))
                        impact = 3

                    elif action == "T1003_ROOTKIT":
                        fname = os.path.join(TARGET_DIR, f".sys_shadow_{timestamp}_{rand_suffix}")
                        with open(fname, 'w') as f: f.write("uid=0(root)")
                        impact = 5

                    elif action == "T1589_LURK":
                        impact = 0
                except OSError as e:
                    # Maybe we hit a trap or permission issue
                    trapped = True
                    logger.warning(f"Attack thwarted/trapped: {e}")

                # 4. REWARDS
                reward = 0
                if impact > 0: reward = R_IMPACT
                if current_alert >= 4 and action == "T1589_LURK": reward = R_STEALTH
                if current_alert == MAX_ALERT and impact > 0: reward = R_CRITICAL
                if trapped: reward = P_TRAPPED

                # 5. LEARN (Experience Replay)
                self.replay_buffer.push(state_key, action, reward, state_key)
                self.learn()

                if self.iteration_count % sync_interval == 0:
                    self.sync_memory()

                # 6. TRIGGER ALERTS
                if impact > 0 and random.random() > 0.5:
                    new_level = min(MAX_ALERT, current_alert + 1)
                    if new_level != current_alert:
                         self.state_manager.update_war_state({'blue_alert_level': new_level})

                logger.info(f"State: {state_key} | Tech: {action} | Impact: {impact} | Q(avg): {self.get_q_value(state_key, action):.2f}")

                time.sleep(random.uniform(0.5, 1.5))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

def engage_offense():
    bot = RedTeamer()
    bot.engage()

if __name__ == "__main__":
    engage_offense()
