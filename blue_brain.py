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
import collections
from typing import Dict, Any, List, Deque

import utils

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "blue_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
WATCH_DIR = "/tmp"

# Make sure we identify as friendly
os.environ["WAR_ROOM_ROLE"] = "BLUE"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE", "DEPLOY_TRAP"]
MIN_EPSILON = 0.01

# --- REWARD CONFIGURATION (AI PERSONALITY) ---
R_MITIGATION = 25       # Reward for killing a threat
R_PATIENCE = 10         # Reward for waiting when safe (saves CPU)
R_TRAP = 50             # Reward for Red Team triggering a honeypot
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

        # Anomaly Detection: Sliding window of file counts
        self.threat_history: Deque[int] = collections.deque(maxlen=10)
        self.traps_deployed = False

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

    def detect_anomaly(self, current_threat_count: int) -> bool:
        """Detects sudden spikes in threat activity."""
        self.threat_history.append(current_threat_count)
        if len(self.threat_history) < 3: return False

        avg = sum(self.threat_history) / len(self.threat_history)
        if current_threat_count > avg * 2 and current_threat_count > 2:
            return True
        return False

    def deploy_nasty_defenses(self):
        """Deploys Tar Pits and Logic Bombs."""
        if not os.path.exists(WATCH_DIR): return

        # Tar Pit (looks like a log file)
        utils.create_tar_pit(os.path.join(WATCH_DIR, "system_access.log"))

        # Logic Bomb / Obfuscated Honeypot (looks like shadow file)
        utils.create_logic_bomb(os.path.join(WATCH_DIR, "shadow_backup"))

        # Another decoy
        utils.create_logic_bomb(os.path.join(WATCH_DIR, "sys_config.dat"))

        self.traps_deployed = True
        logger.info("NASTY DEFENSES DEPLOYED: Tar Pits & Logic Bombs Active.")

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

                anomaly_detected = self.detect_anomaly(threat_count)
                if anomaly_detected:
                    logger.warning("ANOMALY DETECTED: Threat Surge!")
                    if current_alert < MAX_ALERT:
                        self.state_manager.update_war_state({'blue_alert_level': min(MAX_ALERT, current_alert + 1)})

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

                # 4. EXECUTION
                mitigated = 0

                if action == "DEPLOY_TRAP":
                    if not self.traps_deployed:
                        self.deploy_nasty_defenses()

                elif action == "SIGNATURE_SCAN":
                    for t in visible_threats:
                        if utils.is_tar_pit(t): continue # Don't delete our own traps unintentionally
                        try: os.remove(t); mitigated += 1
                        except: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        # Avoid scanning our own traps!
                        if utils.is_tar_pit(t) or utils.is_honeypot(t):
                            continue

                        entropy = 0.0
                        try:
                            if not os.path.islink(t):
                                # Use safe read with timeout to avoid accidental stuck if logic fails
                                # Though we rely on 'is_tar_pit' check primarily
                                data = utils.safe_file_read(t, timeout=0.1)
                                entropy = utils.calculate_entropy(data)
                        except Exception:
                            entropy = 0.0

                        if ".sys" in t or entropy > 3.5:
                            try: os.remove(t); mitigated += 1
                            except: pass

                # 5. REWARDS
                reward = 0
                if mitigated > 0: reward = R_MITIGATION
                if action == "DEPLOY_TRAP" and not self.traps_deployed: reward = R_TRAP
                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = P_WASTE
                if current_alert >= 4 and action == "OBSERVE": reward = R_PATIENCE
                if action == "IGNORE" and threat_count > 0: reward = P_NEGLIGENCE
                if anomaly_detected and action == "HEURISTIC_SCAN": reward += 20

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
