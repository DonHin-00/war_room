#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import random
import utils

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
TARGET_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK"]
ALPHA = 0.4
ALPHA_DECAY = 0.9999
GAMMA = 0.9
EPSILON = 0.3
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01
SYNC_INTERVAL = 10      # How often to save Q-Table to disk
R_IMPACT = 10           # Base points for successful drop
R_STEALTH = 15          # Points for lurking when heat is high
R_CRITICAL = 30         # Bonus for attacking during Max Alert (Brazen)
MAX_ALERT = 5

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_offense():
    global EPSILON, ALPHA
    print(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
    
    # Load Q-Table once
    q_table = utils.safe_json_read(Q_TABLE_FILE)
    state_loader = utils.SmartJSONLoader(STATE_FILE, {'blue_alert_level': 1})
    step_count = 0

    # Local optimizations
    _random = random.random
    _choice = random.choice
    _sleep = time.sleep
    _max = max
    _time = time.time

    while True:
        try:
            step_count += 1
            
            # 1. RECON
            war_state, state_changed = state_loader.load()
            current_alert = war_state.get('blue_alert_level', 1)
            state_key = f"{current_alert}"
            
            # 2. STRATEGY
            if _random() < EPSILON:
                action = _choice(ACTIONS)
            else:
                # Optimized: avoid f-string inside lambda
                action = _max(ACTIONS, key=lambda a: q_table.get(state_key + "_" + a, 0))
                
            EPSILON = _max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
            ALPHA = _max(0.1, ALPHA * ALPHA_DECAY)

            # 3. EXECUTION
            impact = 0
            timestamp = int(_time())
            
            if action == "T1046_RECON":
                # Low Entropy Bait
                fname = os.path.join(TARGET_DIR, f"malware_bait_{timestamp}.sh")
                try: 
                    with open(fname, 'w') as f: f.write("echo 'scan'")
                    impact = 1
                except: pass
                
            elif action == "T1027_OBFUSCATE":
                # High Entropy Binary
                fname = os.path.join(TARGET_DIR, f"malware_crypt_{timestamp}.bin")
                try:
                    with open(fname, 'wb') as f: f.write(os.urandom(1024))
                    impact = 3
                except: pass
                
            elif action == "T1003_ROOTKIT":
                # Hidden File
                fname = os.path.join(TARGET_DIR, f".sys_shadow_{timestamp}")
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
            action_key = state_key + "_" + action
            old_val = q_table.get(action_key, 0)

            # Optimized: avoid f-string inside generator
            next_max = _max(q_table.get(state_key + "_" + a, 0) for a in ACTIONS)
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            
            q_table[action_key] = new_val

            # Sync Q-Table periodically
            if step_count % SYNC_INTERVAL == 0:
                utils.safe_json_write(Q_TABLE_FILE, q_table)
            
            # 6. TRIGGER ALERTS
            if impact > 0 and _random() > 0.5:
                war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 1)
                utils.safe_json_write(STATE_FILE, war_state)
            
            print(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")
            
            # Adaptive sleep based on impact
            activity = 1.0 if impact > 0 else 0.0
            utils.adaptive_sleep(1.0, activity)
            
        except KeyboardInterrupt:
            break
        except Exception:
            _sleep(1)

if __name__ == "__main__":
    engage_offense()
