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

    # Track the last payload: (filename, pid)
    # If PID is still alive or File exists, it survived.
    last_payload = None
    
    while True:
        try:
            # 1. RECON
            war_state = access_memory(config.PATHS['STATE_FILE'])
            if not war_state: war_state = {'blue_alert_level': 1}
            q_table = access_memory(config.PATHS['RED_Q_TABLE'])
            
            current_alert = war_state.get('blue_alert_level', 1)

            # Check if last attack survived
            attack_survived = 0
            if last_payload:
                fname, pid = last_payload
                file_exists = os.path.exists(fname)
                process_alive = False

                if pid:
                    # Check if process is still running
                    try:
                        os.kill(pid, 0)
                        process_alive = True
                    except OSError:
                        process_alive = False

                if file_exists or process_alive:
                    attack_survived = 1

            # Smart State: Alert + Survival Status
            state_key = f"{current_alert}_{attack_survived}"
            
            # 2. STRATEGY
            if random.random() < epsilon:
                action = random.choice(ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                action = max(known, key=known.get)

            # 3. EXECUTION (REAL EMULATION)
            impact = 0
            target_dir = config.PATHS['TARGET_DIR']
            current_drop = None
            spawned_pid = None
            
            if action == "T1046_RECON":
                # Real Recon: Script that lists files recursively (Disk Recon)
                fname = os.path.join(target_dir, f"malware_recon_{int(time.time())}.py")
                try: 
                    with open(fname, 'w') as f:
                        f.write("import os, time\n")
                        f.write("while True:\n")
                        f.write(f"    with open('{os.path.join(target_dir, 'recon_log.txt')}', 'w') as log:\n")
                        f.write("        for root, dirs, files in os.walk('.'):\n")
                        f.write("            for name in files: log.write(os.path.join(root, name) + '\\n')\n")
                        f.write("    time.sleep(5)\n")

                    # Execute it
                    proc = subprocess.Popen([sys.executable, fname], cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    spawned_pid = proc.pid
                    impact = 2
                    current_drop = fname
                except: pass
                
            elif action == "T1027_OBFUSCATE":
                # Real Obfuscation: Self-modifying / High Entropy script
                fname = os.path.join(target_dir, f"malware_crypt_{int(time.time())}.py")
                try:
                    # Write a script that just sleeps but has junk data appended to increase entropy
                    with open(fname, 'w') as f:
                        f.write("import time\n")
                        f.write("time.sleep(60)\n")
                        f.write("#" + "A" * 1024 + "\n") # High entropy junk

                    proc = subprocess.Popen([sys.executable, fname], cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    spawned_pid = proc.pid
                    impact = 3
                    current_drop = fname
                except: pass
                
            elif action == "T1003_ROOTKIT":
                # Persistence: create a hidden file that monitors its own deletion and recreates itself
                fname = os.path.join(target_dir, f".sys_persist_{int(time.time())}.py")
                try:
                    with open(fname, 'w') as f:
                        f.write("import time, os\n")
                        f.write(f"me = '{fname}'\n")
                        f.write("while True:\n")
                        f.write("    if not os.path.exists(me):\n")
                        f.write("        with open(me, 'w') as f: f.write('I am immortal')\n")
                        f.write("    time.sleep(1)\n")

                    proc = subprocess.Popen([sys.executable, fname], cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    spawned_pid = proc.pid
                    impact = 5
                    current_drop = fname
                except: pass

            elif action == "T1059_COMMAND_SCRIPTING":
                # Network Listener: Opens a real port on localhost (high port)
                fname = os.path.join(target_dir, f"malware_c2_{int(time.time())}.py")
                port = random.randint(10000, 60000)
                try:
                    with open(fname, 'w') as f:
                        f.write("import socket, time\n")
                        f.write(f"s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n")
                        f.write(f"s.bind(('127.0.0.1', {port}))\n")
                        f.write("s.listen(1)\n")
                        f.write("while True: time.sleep(1)\n")

                    proc = subprocess.Popen([sys.executable, fname], cwd=target_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    spawned_pid = proc.pid
                    impact = 4
                    current_drop = fname
                except: pass
                
            elif action == "T1589_LURK":
                impact = 0
                if last_payload:
                    current_drop = last_payload[0]
                    spawned_pid = last_payload[1]

            # 4. REWARDS
            reward = 0
            if impact > 0: reward = config.RED['REWARDS']['IMPACT']
            if current_alert >= 4 and action == "T1589_LURK": reward = config.RED['REWARDS']['STEALTH']
            if current_alert == config.SIMULATION['MAX_ALERT'] and impact > 0: reward = config.RED['REWARDS']['CRITICAL']

            # Bonus: If previous attack survived
            if attack_survived and action != "T1589_LURK":
                reward += 10

            # Penalty: If dead
            if not attack_survived and last_payload is not None and action != "T1589_LURK":
                reward -= 10

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

            if current_drop:
                last_payload = (current_drop, spawned_pid)
            
            # Decay Hyperparameters
            epsilon = max(HP['MIN_EPSILON'], epsilon * HP['EPSILON_DECAY'])
            alpha = max(0.1, alpha * HP['ALPHA_DECAY'])
            
            # 6. TRIGGER ALERTS
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
