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

# --- MAIN LOOP ---

def engage_defense():
    # Load AI Config
    EPSILON = config.BLUE['HYPERPARAMETERS']['EPSILON']
    ALPHA = config.BLUE['HYPERPARAMETERS']['ALPHA']
    MIN_EPSILON = config.BLUE['HYPERPARAMETERS']['MIN_EPSILON']
    EPSILON_DECAY = config.BLUE['HYPERPARAMETERS']['EPSILON_DECAY']
    ALPHA_DECAY = config.BLUE['HYPERPARAMETERS']['ALPHA_DECAY']
    ACTIONS = config.BLUE['ACTIONS']
    GAMMA = config.BLUE['HYPERPARAMETERS']['GAMMA']

    print(f"\033[96m[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61\033[0m")
    
    while True:
        try:
            # 1. PREPARATION
            war_state = access_memory(config.PATHS['STATE_FILE'])
            if not war_state: war_state = {'blue_alert_level': 1}
            q_table = access_memory(config.PATHS['BLUE_Q_TABLE'])
            
            current_alert = war_state.get('blue_alert_level', 1)
            
            # 2. DETECTION
            visible_threats = glob.glob(os.path.join(config.PATHS['WATCH_DIR'], 'malware_*'))
            hidden_threats = glob.glob(os.path.join(config.PATHS['WATCH_DIR'], '.sys_*'))
            all_threats = visible_threats + hidden_threats
            
            threat_count = len(all_threats)
            state_key = f"{current_alert}_{threat_count}"
            
            # 3. DECISION
            if random.random() < EPSILON:
                action = random.choice(ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                action = max(known, key=known.get)
            
            EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
            ALPHA = max(0.1, ALPHA * ALPHA_DECAY)

            # 4. ERADICATION
            mitigated = 0
            
            if action == "SIGNATURE_SCAN":
                for t in visible_threats:
                    try: os.remove(t); mitigated += 1
                    except: pass
                    
            elif action == "HEURISTIC_SCAN":
                for t in all_threats:
                    if ".sys" in t or utils.calculate_entropy(t) > 3.5:
                        try: os.remove(t); mitigated += 1
                        except: pass
            
            elif action == "OBSERVE": pass
            elif action == "IGNORE": pass

            # 5. REWARD CALCULATION
            reward = 0
            if mitigated > 0: reward = config.BLUE['REWARDS']['MITIGATION']
            if action == "HEURISTIC_SCAN" and threat_count == 0: reward = config.BLUE['REWARDS']['WASTE']
            if current_alert >= 4 and action == "OBSERVE": reward = config.BLUE['REWARDS']['PATIENCE']
            if action == "IGNORE" and threat_count > 0: reward = config.BLUE['REWARDS']['NEGLIGENCE']
            
            # 6. LEARN
            old_val = q_table.get(f"{state_key}_{action}", 0)
            next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            q_table[f"{state_key}_{action}"] = new_val
            access_memory(config.PATHS['BLUE_Q_TABLE'], q_table)
            
            # 7. UPDATE WAR STATE
            if mitigated > 0 and current_alert < config.SIMULATION['MAX_ALERT']:
                war_state['blue_alert_level'] = min(config.SIMULATION['MAX_ALERT'], current_alert + 1)
            elif mitigated == 0 and current_alert > config.SIMULATION['MIN_ALERT'] and action == "OBSERVE":
                war_state['blue_alert_level'] = max(config.SIMULATION['MIN_ALERT'], current_alert - 1)
                
            access_memory(config.PATHS['STATE_FILE'], war_state)
            
            # LOG
            icon = "🛡️" if mitigated == 0 else "⚔️"
            print(f"\033[94m[BLUE AI]\033[0m {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")
            
            time.sleep(0.5 if current_alert >= 4 else 1.0)

        except KeyboardInterrupt:
            break
        except Exception as e:
            time.sleep(1)

if __name__ == "__main__":
    engage_defense()
