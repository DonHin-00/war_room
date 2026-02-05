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
import traceback
import logging
import subprocess
import socket
import sys
import glob

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

def assimilate_swarm_intel(target_dir, memory, state_key):
    """Read feedback from dead mini-agents and learn from them."""
    pattern = os.path.join(target_dir, "swarm_feedback_*.json")
    feedback_files = glob.glob(pattern)

    assimilated_count = 0
    for fpath in feedback_files:
        try:
            data = utils.safe_json_read(fpath)
            if data:
                # Assimilate: "My children taught me this"
                # We map swarm action "SWARM_NOISE" to "T1588_SWARM_SPAWN" for learning purposes
                # Or we treat it as generic success/fail for the current state.
                reward = data.get('reward', 0)

                # Add to memory: (current_state, SPAWN_ACTION, reward, current_state)
                # It's a bit self-referential but reinforcing "Spawning is good if children succeed"
                memory.append((state_key, "T1588_SWARM_SPAWN", reward, state_key))
                assimilated_count += 1

            os.remove(fpath) # Cleanup the dead
        except: pass
    return assimilated_count

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
    last_dropped_file = None

    # Path to the mini-agent script (assumed to be in same dir as this script)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    mini_agent_script = os.path.join(base_dir, "mini_red.py")
    
    while True:
        try:
            # 1. RECON
            war_state = access_memory(config.PATHS['STATE_FILE'])
            if not war_state: war_state = {'blue_alert_level': 1}
            q_table = access_memory(config.PATHS['RED_Q_TABLE'])
            
            current_alert = war_state.get('blue_alert_level', 1)

            # Check if last attack survived
            attack_survived = 0
            if last_dropped_file and os.path.exists(last_dropped_file):
                attack_survived = 1

            state_key = f"{current_alert}_{attack_survived}"

            # 1.5 ASSIMILATE SWARM INTEL
            swarm_reward_count = assimilate_swarm_intel(config.PATHS['TARGET_DIR'], memory, state_key)
            if swarm_reward_count > 0:
                print(f"\033[91m[RED AI] \033[0m 🕷️ Assimilated {swarm_reward_count} swarm reports.")
            
            # 2. STRATEGY
            if random.random() < epsilon:
                action = random.choice(ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                action = max(known, key=known.get)

            # 3. EXECUTION
            impact = 0
            target_dir = config.PATHS['TARGET_DIR']
            current_drop = None
            
            if action == "T1046_RECON":
                fname = os.path.join(target_dir, f"malware_nmap_{int(time.time())}.sh")
                try: 
                    with open(fname, 'w') as f:
                        f.write("#!/bin/bash\nfor ip in $(seq 1 10); do echo 'Scanning 192.168.1.$ip'; done\n")
                    subprocess.Popen(["/bin/bash", fname], cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    impact = 1
                    current_drop = fname
                except: pass
                
            elif action == "T1027_OBFUSCATE":
                fname = os.path.join(target_dir, f"malware_crypt_{int(time.time())}.py")
                try:
                    with open(fname, 'w') as f:
                        f.write("import time\ntime.sleep(60)\n#" + "A" * 512 + "\n")
                    subprocess.Popen([sys.executable, fname], cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    impact = 3
                    current_drop = fname
                except: pass
                
            elif action == "T1003_ROOTKIT":
                fname = os.path.join(target_dir, f".sys_ld_preload_{int(time.time())}")
                try:
                    with open(fname, 'w') as f: f.write("/usr/local/lib/librootkit.so\n")
                    impact = 5
                    current_drop = fname
                except: pass

            elif action == "T1059_COMMAND_SCRIPTING":
                fname = os.path.join(target_dir, f"malware_c2_{int(time.time())}.py")
                try:
                    with open(fname, 'w') as f:
                        f.write("import time; time.sleep(100)") # Simple placeholder for now
                    subprocess.Popen([sys.executable, fname], cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    impact = 4
                    current_drop = fname
                except: pass

            elif action == "T1588_SWARM_SPAWN":
                # Spawn 3 mini-agents
                for i in range(3):
                    feedback_file = os.path.join(target_dir, f"swarm_feedback_{int(time.time())}_{i}.json")
                    subprocess.Popen([sys.executable, mini_agent_script, target_dir, feedback_file],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                impact = 2 # Initial impact of spawning
                current_drop = None # Swarm agents are fire-and-forget
                
            elif action == "T1589_LURK":
                impact = 0
                current_drop = last_dropped_file

            # 4. REWARDS
            reward = 0
            if impact > 0: reward = config.RED['REWARDS']['IMPACT']
            if current_alert >= 4 and action == "T1589_LURK": reward = config.RED['REWARDS']['STEALTH']
            if current_alert == config.SIMULATION['MAX_ALERT'] and impact > 0: reward = config.RED['REWARDS']['CRITICAL']

            if attack_survived and action != "T1589_LURK": reward += 5
            if not attack_survived and last_dropped_file is not None and action != "T1589_LURK": reward -= 5

            # 5. LEARN & MEMORIZE
            if last_state_key is not None and last_action is not None:
                memory.append((last_state_key, last_action, reward, state_key))

                old_val = q_table.get(f"{last_state_key}_{last_action}", 0)
                next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + alpha * (reward + HP['GAMMA'] * next_max - old_val)
                q_table[f"{last_state_key}_{last_action}"] = new_val

                q_table = experience_replay(memory, HP['BATCH_SIZE'], q_table, alpha, HP['GAMMA'], ACTIONS)

                access_memory(config.PATHS['RED_Q_TABLE'], q_table)

            last_state_key = state_key
            last_action = action
            last_dropped_file = current_drop
            
            epsilon = max(HP['MIN_EPSILON'], epsilon * HP['EPSILON_DECAY'])
            alpha = max(0.1, alpha * HP['ALPHA_DECAY'])
            
            if impact > 0 and random.random() > 0.5:
                war_state['blue_alert_level'] = min(config.SIMULATION['MAX_ALERT'], current_alert + 1)
                access_memory(config.PATHS['STATE_FILE'], war_state)
            
            curr_q = q_table.get(f"{state_key}_{action}", 0)
            print(f"\033[91m[RED AI] \033[0m 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {curr_q:.2f}")
            
            time.sleep(random.uniform(1.0, 2.0))
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"CRITICAL ERROR in Red Brain: {e}")
            logging.error(traceback.format_exc())
            time.sleep(1)

if __name__ == "__main__":
    engage_offense()
