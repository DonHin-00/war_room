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
import signal
import sys

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

# --- UTILITIES ---
def access_memory(filepath, data=None):
    """
    Helper for JSON I/O.
    """
    if data is not None:
        try:
            # Atomic write simulation (simple version)
            # For robust production use, consider using fcntl locking from utils.py
            # or writing to a temp file and renaming.
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"{C_RED}[ERROR] Failed to write {filepath}: {e}{C_RESET}")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

class RedTeamer:
    def __init__(self):
        self.alpha = 0.4
        self.alpha_decay = 0.9999
        self.gamma = 0.9
        self.epsilon = 0.3
        self.epsilon_decay = 0.995

        self.q_table = {}
        self.running = True
        self.iteration_count = 0

        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def load_memory(self):
        self.q_table = access_memory(Q_TABLE_FILE)
        print(f"{C_RED}[SYSTEM] Memory Loaded. Q-Table Size: {len(self.q_table)}{C_RESET}")

    def sync_memory(self):
        access_memory(Q_TABLE_FILE, self.q_table)

    def shutdown(self, signum, frame):
        print(f"\n{C_RED}[SYSTEM] Shutting down... Syncing memory.{C_RESET}")
        self.sync_memory()
        self.running = False
        sys.exit(0)

    def engage(self):
        print(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
        self.load_memory()

        while self.running:
            try:
                self.iteration_count += 1
                
                # 1. RECON
                war_state = access_memory(STATE_FILE)
                if not war_state: war_state = {'blue_alert_level': 1}
                
                current_alert = war_state.get('blue_alert_level', 1)
                state_key = f"{current_alert}"
                
                # 2. STRATEGY
                if random.random() < self.epsilon:
                    action = random.choice(ACTIONS)
                else:
                    known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                    action = max(known, key=known.get)

                self.epsilon = max(MIN_EPSILON, self.epsilon * self.epsilon_decay)
                self.alpha = max(0.1, self.alpha * self.alpha_decay)

                # 3. EXECUTION
                impact = 0

                if action == "T1046_RECON":
                    # Low Entropy Bait
                    fname = os.path.join(TARGET_DIR, f"malware_bait_{int(time.time())}.sh")
                    try:
                        with open(fname, 'w') as f: f.write("echo 'scan'")
                        impact = 1
                    except: pass

                elif action == "T1027_OBFUSCATE":
                    # High Entropy Binary
                    fname = os.path.join(TARGET_DIR, f"malware_crypt_{int(time.time())}.bin")
                    try:
                        with open(fname, 'wb') as f: f.write(os.urandom(1024))
                        impact = 3
                    except: pass

                elif action == "T1003_ROOTKIT":
                    # Hidden File
                    fname = os.path.join(TARGET_DIR, f".sys_shadow_{int(time.time())}")
                    try:
                        with open(fname, 'w') as f: f.write("uid=0(root)")
                        impact = 5
                    except: pass

                elif action == "T1589_LURK":
                    impact = 0

                # 4. REWARDS
                reward = 0
                if impact > 0: reward = R_IMPACT
                if current_alert >= 4 and action == "T1589_LURK": reward = R_STEALTH
                if current_alert == MAX_ALERT and impact > 0: reward = R_CRITICAL

                # 5. LEARN
                old_val = self.q_table.get(f"{state_key}_{action}", 0)
                next_max = max([self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)

                self.q_table[f"{state_key}_{action}"] = new_val

                # Occasional Sync
                if self.iteration_count % SYNC_INTERVAL == 0:
                    self.sync_memory()

                # 6. TRIGGER ALERTS
                if impact > 0 and random.random() > 0.5:
                    war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 1)
                    access_memory(STATE_FILE, war_state)

                print(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")

                time.sleep(random.uniform(0.5, 1.5))

            except KeyboardInterrupt:
                self.shutdown(None, None)
            except Exception as e:
                # print(f"Error: {e}")
                time.sleep(1)

def engage_offense():
    """Legacy entry point for compatibility"""
    bot = RedTeamer()
    bot.engage()

if __name__ == "__main__":
    engage_offense()
