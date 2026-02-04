#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix

This module implements the Red Team AI, an automated adversary that simulates
APT (Advanced Persistent Threat) behaviors. It uses Q-Learning to adapt its
strategy based on the defensive posture of the Blue Team.
"""

import os
import time
import json
import random
import signal
import sys
import logging
from typing import Dict, Any, Optional

# Import shared utilities if available
try:
    import utils
except ImportError:
    utils = None

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
TARGET_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK"]
MIN_EPSILON = 0.01

# --- REWARD CONFIGURATION (ATTACKER PROFILE) ---
R_IMPACT = 10           # Base points for successful drop
R_STEALTH = 15          # Points for lurking when heat is high
R_CRITICAL = 30         # Bonus for attacking during Max Alert (Brazen)
MAX_ALERT = 5

# --- PERFORMANCE CONFIGURATION ---
SYNC_INTERVAL = 10      # How often to sync Q-Table to disk

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
    """
    def __init__(self):
        self.state_cache: Dict[str, Any] = {}
        self.state_mtime: float = 0.0

    def load_json(self, filepath: str) -> Dict[str, Any]:
        """Safely loads JSON data from a file."""
        if utils:
            # Use utils for locking if available, though read lock might be overkill for simple reads
            # We stick to simple read for speed unless writing
            pass

        if not os.path.exists(filepath):
            return {}

        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to read {filepath}: {e}")
            return {}

    def save_json(self, filepath: str, data: Dict[str, Any]) -> None:
        """Safely saves JSON data to a file using atomic write patterns."""
        if utils:
            try:
                # Use utils.safe_file_write which handles locking
                json_str = json.dumps(data, indent=4)
                utils.safe_file_write(filepath, json_str)
                return
            except Exception as e:
                logger.error(f"Utils save failed: {e}")
                # Fallback to local logic

        try:
            # Atomic write simulation: write to temp then rename
            temp_path = filepath + ".tmp"
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, filepath)
        except IOError as e:
            logger.error(f"Failed to write {filepath}: {e}")

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
        # Update cache immediately
        self.state_cache = current
        try:
            self.state_mtime = os.stat(STATE_FILE).st_mtime
        except OSError:
            self.state_mtime = time.time()


class RedTeamer:
    """
    The Red Team AI Agent.
    """
    def __init__(self):
        self.alpha = 0.4
        self.alpha_decay = 0.9999
        self.gamma = 0.9
        self.epsilon = 0.3
        self.epsilon_decay = 0.995

        self.q_table: Dict[str, float] = {}
        self.running = True
        self.iteration_count = 0

        self.state_manager = StateManager()

        # Signal handling for graceful shutdown
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
        logger.info("Red Team AI Initialized. APT Framework: ACTIVE")
        self.load_memory()

        # Ensure target directory exists
        if not os.path.exists(TARGET_DIR):
            try:
                os.makedirs(TARGET_DIR)
            except OSError:
                pass

        while self.running:
            try:
                self.iteration_count += 1
                
                # 1. RECON (Optimized with mtime cache)
                war_state = self.state_manager.get_war_state()
                if not war_state:
                    war_state = {'blue_alert_level': 1}
                
                current_alert = war_state.get('blue_alert_level', 1)
                # Optimize key generation? f-strings are fast enough usually,
                # but could use tuple if dict supported it cleanly with JSON.
                # Sticking to string for compatibility.
                state_key = f"{current_alert}"

                # 2. STRATEGY
                if random.random() < self.epsilon:
                    action = random.choice(ACTIONS)
                else:
                    # Optimized max finding
                    # Pre-calculate keys to avoid repeated f-string gen in loop?
                    # The number of actions is small (4), so overhead is low.
                    best_action = None
                    max_q = -float('inf')

                    for a in ACTIONS:
                        q = self.q_table.get(f"{state_key}_{a}", 0.0)
                        if q > max_q:
                            max_q = q
                            best_action = a
                    action = best_action

                # Decay hyperparameters
                self.epsilon = max(MIN_EPSILON, self.epsilon * self.epsilon_decay)
                self.alpha = max(0.1, self.alpha * self.alpha_decay)

                # 3. EXECUTION
                impact = 0
                fname = ""

                try:
                    if action == "T1046_RECON":
                        fname = os.path.join(TARGET_DIR, f"malware_bait_{int(time.time())}_{random.randint(1000,9999)}.sh")
                        with open(fname, 'w') as f: f.write("echo 'scan'")
                        impact = 1

                    elif action == "T1027_OBFUSCATE":
                        fname = os.path.join(TARGET_DIR, f"malware_crypt_{int(time.time())}_{random.randint(1000,9999)}.bin")
                        with open(fname, 'wb') as f: f.write(os.urandom(1024))
                        impact = 3

                    elif action == "T1003_ROOTKIT":
                        fname = os.path.join(TARGET_DIR, f".sys_shadow_{int(time.time())}_{random.randint(1000,9999)}")
                        with open(fname, 'w') as f: f.write("uid=0(root)")
                        impact = 5

                    elif action == "T1589_LURK":
                        impact = 0
                except OSError as e:
                    logger.warning(f"Attack failed: {e}")

                # 4. REWARDS
                reward = 0
                if impact > 0: reward = R_IMPACT
                if current_alert >= 4 and action == "T1589_LURK": reward = R_STEALTH
                if current_alert == MAX_ALERT and impact > 0: reward = R_CRITICAL

                # 5. LEARN
                # Q(s,a) = Q(s,a) + alpha * (R + gamma * max(Q(s', a')) - Q(s,a))
                # Here s' is assumed to be same state for simplicity in original code,
                # or rather, it updates based on immediate reward.
                # Ideally, we should observe next state, but we follow original logic.

                current_q_key = f"{state_key}_{action}"
                old_val = self.q_table.get(current_q_key, 0.0)

                # Find max Q for next step (bootstrap)
                # In this simple model, next state isn't explicitly observed before update,
                # so we use current state properties or assume state transition happens later.
                # Original code used `state_key` (current) for next_max, effectively Q-learning on same state loop.
                next_max = -float('inf')
                for a in ACTIONS:
                    q = self.q_table.get(f"{state_key}_{a}", 0.0)
                    if q > next_max: next_max = q

                new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
                self.q_table[current_q_key] = new_val

                # Occasional Sync
                if self.iteration_count % SYNC_INTERVAL == 0:
                    self.sync_memory()

                # 6. TRIGGER ALERTS
                if impact > 0 and random.random() > 0.5:
                    # Update war state directly via manager
                    # Logic: read fresh state (we have cache but need to be careful with increments)
                    # Actually, get_war_state returns cached or fresh.
                    # To be safe for increment, we should force a read or rely on cache + logic.
                    # Best effort: use what we have.
                    new_level = min(MAX_ALERT, current_alert + 1)
                    if new_level != current_alert:
                         self.state_manager.update_war_state({'blue_alert_level': new_level})

                logger.info(f"State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")

                time.sleep(random.uniform(0.5, 1.5))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                logger.error(f"Loop Error: {e}")
                time.sleep(1)

def engage_offense():
    """Legacy entry point for compatibility"""
    bot = RedTeamer()
    bot.engage()

if __name__ == "__main__":
    engage_offense()
