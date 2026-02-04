#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import random
import config
import utils

# --- SYSTEM CONFIGURATION ---
utils.ensure_directories(config.PATHS['TARGET_DIR'])
utils.setup_logging(config.PATHS['LOG_FILE'])

# --- UTILITIES ---
def access_memory(filepath, data=None):
    if data is not None:
        utils.safe_json_write(filepath, data)
    return utils.safe_json_read(filepath)

# --- MAIN LOOP ---

def engage_offense():
    # Load AI Config
    EPSILON = config.RED['HYPERPARAMETERS']['EPSILON']
    ALPHA = config.RED['HYPERPARAMETERS']['ALPHA']
    MIN_EPSILON = config.RED['HYPERPARAMETERS']['MIN_EPSILON']
    EPSILON_DECAY = config.RED['HYPERPARAMETERS']['EPSILON_DECAY']
    ALPHA_DECAY = config.RED['HYPERPARAMETERS']['ALPHA_DECAY']
    ACTIONS = config.RED['ACTIONS']
    GAMMA = config.RED['HYPERPARAMETERS']['GAMMA']

    print(f"\033[91m[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE\033[0m")
    
    while True:
        try:
            # 1. RECON
            war_state = access_memory(config.PATHS['STATE_FILE'])
            if not war_state: war_state = {'blue_alert_level': 1}
            q_table = access_memory(config.PATHS['RED_Q_TABLE'])
            
            current_alert = war_state.get('blue_alert_level', 1)
            state_key = f"{current_alert}"
            
            # 2. STRATEGY
            if random.random() < EPSILON:
                action = random.choice(ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                action = max(known, key=known.get)
                
            EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
            ALPHA = max(0.1, ALPHA * ALPHA_DECAY)

            # 3. EXECUTION
            impact = 0
            target_dir = config.PATHS['TARGET_DIR']
            
            if action == "T1046_RECON":
                # Low Entropy Bait
                fname = os.path.join(target_dir, f"malware_bait_{int(time.time())}.sh")
                try: 
                    with open(fname, 'w') as f: f.write("echo 'scan'")
                    impact = 1
                except: pass
                
            elif action == "T1027_OBFUSCATE":
                # High Entropy Binary
                fname = os.path.join(target_dir, f"malware_crypt_{int(time.time())}.bin")
                try:
                    with open(fname, 'wb') as f: f.write(os.urandom(1024))
                    impact = 3
                except: pass
                
            elif action == "T1003_ROOTKIT":
                # Hidden File
                fname = os.path.join(target_dir, f".sys_shadow_{int(time.time())}")
                try:
                    with open(fname, 'w') as f: f.write("uid=0(root)")
                    impact = 5
                except: pass
                
            elif action == "T1589_LURK":
                impact = 0

            # 4. REWARDS
            reward = 0
            if impact > 0: reward = config.RED['REWARDS']['IMPACT']
            if current_alert >= 4 and action == "T1589_LURK": reward = config.RED['REWARDS']['STEALTH']
            if current_alert == config.SIMULATION['MAX_ALERT'] and impact > 0: reward = config.RED['REWARDS']['CRITICAL']
            
            # 5. LEARN
            old_val = q_table.get(f"{state_key}_{action}", 0)
            next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            
            q_table[f"{state_key}_{action}"] = new_val
            access_memory(config.PATHS['RED_Q_TABLE'], q_table)
            
            # 6. TRIGGER ALERTS
            if impact > 0 and random.random() > 0.5:
                war_state['blue_alert_level'] = min(config.SIMULATION['MAX_ALERT'], current_alert + 1)
                access_memory(config.PATHS['STATE_FILE'], war_state)
            
            print(f"\033[91m[RED AI] \033[0m 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")
            
            time.sleep(random.uniform(0.5, 1.5))
            
        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    engage_offense()
