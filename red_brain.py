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
from collections import deque

# --- SYSTEM CONFIGURATION ---
utils.ensure_directories(config.PATHS['TARGET_DIR'])
utils.setup_logging(config.PATHS['LOG_FILE'])

# --- UTILITIES ---
def access_memory(filepath, data=None):
    if data is not None:
        utils.safe_json_write(filepath, data)
    return utils.safe_json_read(filepath)

# --- REINFORCEMENT LEARNING UTILITIES ---

def experience_replay(memory, batch_size, q_table, alpha, gamma, actions):
    """Train on a batch of past experiences to stabilize learning."""
    if len(memory) < batch_size:
        return q_table

    batch = random.sample(memory, batch_size)
    for state, action, reward, next_state in batch:
        old_val = q_table.get(f"{state}_{action}", 0)
        next_max = max([q_table.get(f"{next_state}_{a}", 0) for a in actions])
        new_val = old_val + alpha * (reward + gamma * next_max - old_val)
        q_table[f"{state}_{action}"] = new_val

    return q_table

# --- MAIN LOOP ---

def engage_offense():
    # Load AI Config
    HP = config.RED['HYPERPARAMETERS']
    ACTIONS = config.RED['ACTIONS']

    epsilon = HP['EPSILON']
    alpha = HP['ALPHA']

    memory = deque(maxlen=HP['MEMORY_SIZE'])

    print(f"\033[91m[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE\033[0m")

    last_state_key = None
    last_action = None
    
    while True:
        try:
            # 1. RECON
            war_state = access_memory(config.PATHS['STATE_FILE'])
            if not war_state: war_state = {'blue_alert_level': 1}
            q_table = access_memory(config.PATHS['RED_Q_TABLE'])
            
            current_alert = war_state.get('blue_alert_level', 1)
            state_key = f"{current_alert}"
            
            # 2. STRATEGY
            if random.random() < epsilon:
                action = random.choice(ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                action = max(known, key=known.get)

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
            
            # 5. LEARN & MEMORIZE
            if last_state_key is not None and last_action is not None:
                # Add to memory: (s, a, r, s')
                memory.append((last_state_key, last_action, reward, state_key))

                # Update Q-table immediately (Online Learning)
                old_val = q_table.get(f"{last_state_key}_{last_action}", 0)
                next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + alpha * (reward + HP['GAMMA'] * next_max - old_val)
                q_table[f"{last_state_key}_{last_action}"] = new_val

                # Experience Replay (Batch Learning)
                q_table = experience_replay(memory, HP['BATCH_SIZE'], q_table, alpha, HP['GAMMA'], ACTIONS)

                access_memory(config.PATHS['RED_Q_TABLE'], q_table)

            last_state_key = state_key
            last_action = action
            
            # Decay Hyperparameters
            epsilon = max(HP['MIN_EPSILON'], epsilon * HP['EPSILON_DECAY'])
            alpha = max(0.1, alpha * HP['ALPHA_DECAY'])
            
            # 6. TRIGGER ALERTS
            if impact > 0 and random.random() > 0.5:
                war_state['blue_alert_level'] = min(config.SIMULATION['MAX_ALERT'], current_alert + 1)
                access_memory(config.PATHS['STATE_FILE'], war_state)
            
            curr_q = q_table.get(f"{state_key}_{action}", 0)
            print(f"\033[91m[RED AI] \033[0m 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {curr_q:.2f}")
            
            time.sleep(random.uniform(0.5, 1.5))
            
        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    engage_offense()
