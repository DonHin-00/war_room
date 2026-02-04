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
import config
import utils
from collections import deque
import traceback
import logging
import signal
import subprocess

# --- SYSTEM CONFIGURATION ---
utils.ensure_directories(config.PATHS['WATCH_DIR'])
utils.setup_logging(config.PATHS['LOG_FILE'])

# --- MEMORY CACHE ---
MEMORY_CACHE = {}

def access_memory(filepath, data=None):
    """Atomic JSON I/O with Caching via Utils."""
    global MEMORY_CACHE

    if data is not None:
        if utils.safe_json_write(filepath, data):
            if os.path.exists(filepath):
                 MEMORY_CACHE[filepath] = {'mtime': os.path.getmtime(filepath), 'data': data}

    if os.path.exists(filepath):
        try:
            current_mtime = os.path.getmtime(filepath)
            if filepath in MEMORY_CACHE and MEMORY_CACHE[filepath]['mtime'] == current_mtime:
                return MEMORY_CACHE[filepath]['data'].copy()

            content = utils.safe_json_read(filepath)
            MEMORY_CACHE[filepath] = {'mtime': current_mtime, 'data': content}
            return content.copy()
        except: return {}
    return {}

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

def get_suspicious_pids(war_zone_dir):
    """Find PIDs running scripts inside the war zone."""
    # Since we can't trust 'ps' output parsing easily across all envs, and we want to emulate detection.
    # We will use 'pgrep -f war_zone_dir' to find processes running from our sandbox.
    # This is a realistic 'Heuristic' for process detection in a constrained environment.
    suspicious_pids = []
    try:
        # Check for python scripts running in the war zone
        cmd = ["pgrep", "-f", war_zone_dir]
        # Note: pgrep -f matches the full command line.
        # Red Team launches: python3 /path/to/war_zone_X/malware.py

        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        if result.returncode == 0:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid.strip():
                    suspicious_pids.append(int(pid))
    except: pass
    return suspicious_pids

def kill_pid(pid):
    """Kill a process by PID."""
    try:
        os.kill(pid, signal.SIGKILL)
        return True
    except: return False

# --- MAIN LOOP ---

def engage_defense():
    # Load AI Config
    HP = config.BLUE['HYPERPARAMETERS']
    ACTIONS = config.BLUE['ACTIONS']

    epsilon = HP['EPSILON']
    alpha = HP['ALPHA']

    memory = deque(maxlen=HP['MEMORY_SIZE'])

    print(f"\033[96m[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61\033[0m")

    last_state_key = None
    last_action = None
    
    while True:
        try:
            # 1. PREPARATION
            war_state = access_memory(config.PATHS['STATE_FILE'])
            if not war_state: war_state = {'blue_alert_level': 1}
            q_table = access_memory(config.PATHS['BLUE_Q_TABLE'])
            
            current_alert = war_state.get('blue_alert_level', 1)
            
            # 2. DETECTION
            # File Detection
            visible_threats = []
            hidden_threats = []

            with os.scandir(config.PATHS['WATCH_DIR']) as entries:
                for entry in entries:
                    if entry.is_file():
                        if entry.name.startswith("malware_"):
                            visible_threats.append(entry.path)
                        elif entry.name.startswith(".sys_"):
                            hidden_threats.append(entry.path)

            # Process Detection
            suspicious_pids = get_suspicious_pids(config.PATHS['WATCH_DIR'])

            has_visible = 1 if visible_threats else 0
            has_hidden = 1 if hidden_threats else 0
            has_process = 1 if suspicious_pids else 0

            threat_count = len(visible_threats) + len(hidden_threats) + len(suspicious_pids)

            # Smart State: Alert + Visible + Hidden + Process
            # We append Process status to state key
            state_key = f"{current_alert}_{has_visible}_{has_hidden}_{has_process}"
            
            # 3. DECISION
            if random.random() < epsilon:
                action = random.choice(ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                action = max(known, key=known.get)
            
            # 4. ERADICATION
            mitigated = 0
            
            if action == "SIGNATURE_SCAN":
                # Signature scan deletes known malware files
                for t in visible_threats:
                    try:
                        os.remove(t)
                        mitigated += 1
                    except: pass
                    
            elif action == "HEURISTIC_SCAN":
                # Heuristic scan deletes hidden files AND kills suspicious processes
                all_files = visible_threats + hidden_threats
                for t in all_files:
                    try:
                        os.remove(t)
                        mitigated += 1
                    except: pass

                for pid in suspicious_pids:
                    if kill_pid(pid):
                        mitigated += 1
            
            elif action == "OBSERVE": pass
            elif action == "IGNORE": pass

            # 5. REWARD CALCULATION
            reward = 0
            if mitigated > 0: reward = config.BLUE['REWARDS']['MITIGATION']
            if action == "HEURISTIC_SCAN" and threat_count == 0: reward = config.BLUE['REWARDS']['WASTE']
            if current_alert >= 4 and action == "OBSERVE": reward = config.BLUE['REWARDS']['PATIENCE']
            if action == "IGNORE" and threat_count > 0: reward = config.BLUE['REWARDS']['NEGLIGENCE']

            # 6. LEARN & MEMORIZE
            if last_state_key is not None and last_action is not None:
                memory.append((last_state_key, last_action, reward, state_key))

                old_val = q_table.get(f"{last_state_key}_{last_action}", 0)
                next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + alpha * (reward + HP['GAMMA'] * next_max - old_val)
                q_table[f"{last_state_key}_{last_action}"] = new_val

                q_table = experience_replay(memory, HP['BATCH_SIZE'], q_table, alpha, HP['GAMMA'], ACTIONS)

                access_memory(config.PATHS['BLUE_Q_TABLE'], q_table)

            last_state_key = state_key
            last_action = action

            # Decay Hyperparameters
            epsilon = max(HP['MIN_EPSILON'], epsilon * HP['EPSILON_DECAY'])
            alpha = max(0.1, alpha * HP['ALPHA_DECAY'])

            # 7. UPDATE WAR STATE
            if mitigated > 0 and current_alert < config.SIMULATION['MAX_ALERT']:
                war_state['blue_alert_level'] = min(config.SIMULATION['MAX_ALERT'], current_alert + 1)
            elif mitigated == 0 and current_alert > config.SIMULATION['MIN_ALERT'] and action == "OBSERVE":
                war_state['blue_alert_level'] = max(config.SIMULATION['MIN_ALERT'], current_alert - 1)
                
            access_memory(config.PATHS['STATE_FILE'], war_state)
            
            # LOG
            icon = "🛡️" if mitigated == 0 else "⚔️"
            curr_q = q_table.get(f"{state_key}_{action}", 0)
            print(f"\033[94m[BLUE AI]\033[0m {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {curr_q:.2f}")
            
            time.sleep(0.5 if current_alert >= 4 else 1.0)

        except KeyboardInterrupt:
            break
        except Exception as e:
            logging.error(f"CRITICAL ERROR in Blue Brain: {e}")
            logging.error(traceback.format_exc())
            time.sleep(1)

if __name__ == "__main__":
    engage_defense()
