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
import sys
import signal
import argparse

# Import utils from current directory
try:
    import utils
except ImportError:
    # If running from a different directory, try to append current dir
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import utils
import config

# --- SYSTEM CONFIGURATION ---
Q_TABLE_FILE = config.PATHS['RED_Q_TABLE']
STATE_FILE = config.PATHS['STATE_FILE']
TARGET_DIR = config.PATHS['BATTLEFIELD']
EVOLUTION_LOG = config.PATHS['EVOLUTION_LOG']

# --- AI HYPERPARAMETERS ---
ACTIONS = config.RED['ACTIONS']
ALPHA = config.HYPERPARAMETERS['ALPHA']
ALPHA_DECAY = config.HYPERPARAMETERS['ALPHA_DECAY']
GAMMA = config.HYPERPARAMETERS['GAMMA']
EPSILON = config.HYPERPARAMETERS['EPSILON']
EPSILON_DECAY = config.HYPERPARAMETERS['EPSILON_DECAY']
MIN_EPSILON = config.HYPERPARAMETERS['MIN_EPSILON']

# --- REWARD CONFIGURATION (ATTACKER PROFILE) ---
R_IMPACT = config.RED['REWARDS']['IMPACT']
R_STEALTH = config.RED['REWARDS']['STEALTH']
R_CRITICAL = config.RED['REWARDS']['CRITICAL']
MAX_ALERT = config.RED['ALERTS']['MAX']

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

# --- UTILITIES ---
def access_memory(filepath, data=None):
    if data is not None:
        utils.safe_json_write(filepath, data)
    return utils.safe_json_read(filepath)

# --- MAIN LOOP ---

class RedTeamer:
    def __init__(self, reset=False):
        self.running = True
        self.q_table = {}
        self.evolution = {}
        self.audit = utils.AuditLogger()

        if reset:
            print(f"{C_RED}[RED AI] Resetting Q-Table...{C_RESET}")
            self.q_table = {}
            self.evolution = {}
            access_memory(Q_TABLE_FILE, self.q_table)
            access_memory(EVOLUTION_LOG, self.evolution)
        else:
            # Load initial Q-table and Evolution Log
            self.q_table = access_memory(Q_TABLE_FILE)
            self.evolution = access_memory(EVOLUTION_LOG)

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        print(f"\n{C_RED}[SYSTEM] Red Team AI Shutting Down...{C_RESET}")
        self.save_state()
        self.running = False
        sys.exit(0)

    def save_state(self):
        access_memory(Q_TABLE_FILE, self.q_table)
        access_memory(EVOLUTION_LOG, self.evolution)

    def log_evolution(self, technique, success):
        """Record the success of a specific technique."""
        if technique not in self.evolution:
            self.evolution[technique] = {'attempts': 0, 'success': 0}

        self.evolution[technique]['attempts'] += 1
        if success:
            self.evolution[technique]['success'] += 1

    def run(self):
        global EPSILON, ALPHA
        print(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")

        while self.running:
            try:
                # 1. RECON
                war_state = access_memory(STATE_FILE)
                if not war_state: war_state = {'blue_alert_level': 1}
                # q_table is now self.q_table
                
                current_alert = war_state.get('blue_alert_level', 1)
                state_key = f"{current_alert}"
                
                # 2. STRATEGY
                if random.random() < EPSILON:
                    action = random.choice(ACTIONS)
                else:
                    known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                    action = max(known, key=known.get)

                EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
                ALPHA = max(0.1, ALPHA * ALPHA_DECAY)

                # 3. EXECUTION
                impact = 0

                if action == "T1046_RECON":
                    # Low Entropy Bait
                    fname = os.path.join(TARGET_DIR, f"malware_bait_{int(time.time())}.sh")
                    try:
                        with open(fname, 'w') as f: f.write("echo 'scan'")
                        impact = 1
                        self.audit.log_event("RED", "ATTACK_BAIT", fname)
                    except: pass
                    self.log_evolution("T1046_RECON", impact > 0)

                elif action == "T1027_OBFUSCATE":
                    # High Entropy Binary
                    # If T1027 has high success rate, maybe increase payload size?
                    payload_size = 1024
                    if self.evolution.get('T1027_OBFUSCATE', {}).get('success', 0) > 5:
                        payload_size = 2048 # Evolve!

                    fname = os.path.join(TARGET_DIR, f"malware_crypt_{int(time.time())}.bin")
                    try:
                        with open(fname, 'wb') as f: f.write(os.urandom(payload_size))
                        impact = 3
                        self.audit.log_event("RED", "ATTACK_OBFUSCATE", fname, {"size": payload_size})
                    except: pass
                    self.log_evolution("T1027_OBFUSCATE", impact > 0)

                elif action == "T1003_ROOTKIT":
                    # Hidden File
                    fname = os.path.join(TARGET_DIR, f".sys_shadow_{int(time.time())}")
                    try:
                        with open(fname, 'w') as f: f.write("uid=0(root)")
                        impact = 5
                        self.audit.log_event("RED", "ATTACK_ROOTKIT", fname)
                    except: pass
                    self.log_evolution("T1003_ROOTKIT", impact > 0)

                elif action == "T1589_LURK":
                    impact = 0
                    self.log_evolution("T1589_LURK", True) # Always successful to lurk

                # 4. REWARDS
                reward = 0
                if impact > 0: reward = R_IMPACT
                if current_alert >= 4 and action == "T1589_LURK": reward = R_STEALTH
                if current_alert == MAX_ALERT and impact > 0: reward = R_CRITICAL

                # 5. LEARN
                old_val = self.q_table.get(f"{state_key}_{action}", 0)
                next_max = max([self.q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)

                self.q_table[f"{state_key}_{action}"] = new_val
                access_memory(Q_TABLE_FILE, self.q_table)

                # 6. TRIGGER ALERTS
                if impact > 0 and random.random() > 0.5:
                    war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 1)
                    access_memory(STATE_FILE, war_state)

                print(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")

                time.sleep(random.uniform(0.5, 1.5))
            
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Reset Q-Table")
    parser.add_argument("--debug", action="store_true", help="Debug mode (unused for now)")
    args = parser.parse_args()

    attacker = RedTeamer(reset=args.reset)
    attacker.run()
