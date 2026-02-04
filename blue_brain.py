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
from typing import Dict, Any, List

import utils

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "blue_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
WATCH_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE"]
MIN_EPSILON = 0.01

# --- REWARD CONFIGURATION (AI PERSONALITY) ---
R_MITIGATION = 25       # Reward for killing a threat
R_PATIENCE = 10         # Reward for waiting when safe (saves CPU)
P_WASTE = -15           # Penalty for scanning empty air (Paranoia)
P_NEGLIGENCE = -50      # Penalty for ignoring active malware
MAX_ALERT = 5
MIN_ALERT = 1

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format=f"{C_BLUE}[%(levelname)s] %(message)s{C_RESET}"
)
logger = logging.getLogger("BlueTeam")

# --- DEFENSIVE UTILITIES ---

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
        """Retrieves the shared war state with mtime caching."""
        if not os.path.exists(STATE_FILE):
            return {'blue_alert_level': 1}
        try:
            mtime = os.stat(STATE_FILE).st_mtime
            if mtime > self.state_mtime:
                self.state_cache = self.load_json(STATE_FILE)
                self.state_mtime = mtime
        except OSError: pass
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

class BlueDefender:
    def __init__(self):
        self.alpha = 0.4
        self.alpha_decay = 0.9999
        self.gamma = 0.9
        self.epsilon = 0.3
        self.epsilon_decay = 0.995

        self.q_table: Dict[str, float] = {}
        self.running = True
        self.state_manager = StateManager()

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def load_memory(self):
        self.q_table = self.state_manager.load_json(Q_TABLE_FILE)
        logger.info(f"Memory Loaded. Q-Table Size: {len(self.q_table)}")

    def sync_memory(self):
        self.state_manager.save_json(Q_TABLE_FILE, self.q_table)

    def shutdown(self, signum, frame):
        logger.info("Shutting down... Syncing memory.")
        self.sync_memory()
        self.running = False
        sys.exit(0)

    def engage(self):
        logger.info("Blue Team AI Initialized. Policy: NIST SP 800-61")
        self.load_memory()

        while self.running:
            try:
                # 1. PREPARATION
                war_state = self.state_manager.get_war_state()
                if not war_state: war_state = {'blue_alert_level': 1}
                current_alert = war_state.get('blue_alert_level', 1)

                # 2. DETECTION
                visible_threats = glob.glob(os.path.join(WATCH_DIR, 'malware_*'))
                hidden_threats = glob.glob(os.path.join(WATCH_DIR, '.sys_*'))
                all_threats = visible_threats + hidden_threats

                threat_count = len(all_threats)
                state_key = f"{current_alert}_{threat_count}"

                # 3. DECISION
                if random.random() < self.epsilon:
                    action = random.choice(ACTIONS)
                else:
                    best_action = None
                    max_q = -float('inf')
                    for a in ACTIONS:
                        q = self.q_table.get(f"{state_key}_{a}", 0.0)
                        if q > max_q:
                            max_q = q
                            best_action = a
                    action = best_action if best_action else random.choice(ACTIONS)

                self.epsilon = max(MIN_EPSILON, self.epsilon * self.epsilon_decay)
                self.alpha = max(0.1, self.alpha * self.alpha_decay)

                # 4. ERADICATION
                mitigated = 0
                if action == "SIGNATURE_SCAN":
                    for t in visible_threats:
                        try: os.remove(t); mitigated += 1
                        except: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        entropy = 0.0
                        try:
                            # Read file content safely for entropy calculation
                            # Note: t is a path, calculate_entropy expects data (str or bytes)
                            if not os.path.islink(t):
                                with open(t, 'rb') as f:
                                    data = f.read()
                                    entropy = utils.calculate_entropy(data)
                        except Exception:
                            entropy = 0.0

                        if ".sys" in t or entropy > 3.5:
                            try: os.remove(t); mitigated += 1
                            except: pass

                # 5. REWARD CALCULATION
                reward = 0
                if mitigated > 0: reward = R_MITIGATION
                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = P_WASTE
                if current_alert >= 4 and action == "OBSERVE": reward = R_PATIENCE
                if action == "IGNORE" and threat_count > 0: reward = P_NEGLIGENCE
                
                # 6. LEARN
                current_q_key = f"{state_key}_{action}"
                old_val = self.q_table.get(current_q_key, 0.0)
                next_max = -float('inf')
                for a in ACTIONS:
                    q = self.q_table.get(f"{state_key}_{a}", 0.0)
                    if q > next_max: next_max = q
                if next_max == -float('inf'): next_max = 0.0

                new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
                self.q_table[current_q_key] = new_val
                self.sync_memory()

                # 7. UPDATE WAR STATE
                if mitigated > 0 and current_alert < MAX_ALERT:
                    self.state_manager.update_war_state({'blue_alert_level': min(MAX_ALERT, current_alert + 1)})
                elif mitigated == 0 and current_alert > MIN_ALERT and action == "OBSERVE":
                    self.state_manager.update_war_state({'blue_alert_level': max(MIN_ALERT, current_alert - 1)})

                icon = "🛡️" if mitigated == 0 else "⚔️"
                logger.info(f"{icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")

                time.sleep(0.5 if current_alert >= 4 else 1.0)

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

def engage_defense():
    bot = BlueDefender()
    bot.engage()

if __name__ == "__main__":
    engage_defense()
