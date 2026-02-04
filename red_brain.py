#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import random
import secrets
import config
import utils

# --- SYSTEM INITIALIZATION ---
utils.check_root()
logger = utils.setup_logging("RedBrain", config.RED_LOG)

# --- AI STATE ---
ALPHA = config.HYPERPARAMETERS['learning_rate']
ALPHA_DECAY = config.HYPERPARAMETERS['learning_rate_decay']
GAMMA = config.HYPERPARAMETERS['discount_factor']
EPSILON = config.HYPERPARAMETERS['epsilon']
EPSILON_DECAY = config.HYPERPARAMETERS['epsilon_decay']
MIN_EPSILON = config.HYPERPARAMETERS['min_epsilon']

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_offense():
    global EPSILON, ALPHA
    logger.info(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
    
    while True:
        try:
            # 1. RECON
            war_state = utils.safe_json_read(config.STATE_FILE, {'blue_alert_level': 1})
            # Input Validation
            if not utils.validate_state(war_state):
                logger.warning("Corrupted state detected, resetting.")
                war_state = {'blue_alert_level': 1}

            q_table = utils.safe_json_read(config.Q_TABLE_RED)
            
            current_alert = war_state.get('blue_alert_level', 1)
            state_key = f"{current_alert}"
            
            # 2. STRATEGY
            if random.random() < EPSILON:
                action = random.choice(config.RED_ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in config.RED_ACTIONS}
                action = max(known, key=known.get)
                
            EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
            ALPHA = max(0.1, ALPHA * ALPHA_DECAY)

            # 3. EXECUTION
            impact = 0
            
            if action == "T1046_RECON":
                # Low Entropy Bait
                fname = os.path.join(config.SIMULATION_DATA_DIR, f"malware_bait_{secrets.token_hex(8)}.sh")
                if utils.secure_create(fname, "echo 'scan'"):
                    impact = 1
                
            elif action == "T1027_OBFUSCATE":
                # High Entropy Binary
                fname = os.path.join(config.SIMULATION_DATA_DIR, f"malware_crypt_{secrets.token_hex(8)}.bin")
                if utils.secure_create(fname, os.urandom(1024), is_binary=True):
                    impact = 3
                
            elif action == "T1003_ROOTKIT":
                # Hidden File
                fname = os.path.join(config.SIMULATION_DATA_DIR, f".sys_shadow_{secrets.token_hex(8)}")
                if utils.secure_create(fname, "uid=0(root)"):
                    impact = 5
                
            elif action == "T1589_LURK":
                impact = 0

            # 4. REWARDS
            reward = 0
            if impact > 0: reward = config.RED_REWARDS['impact']
            if current_alert >= 4 and action == "T1589_LURK": reward = config.RED_REWARDS['stealth']
            if current_alert == config.MAX_ALERT and impact > 0: reward = config.RED_REWARDS['critical']
            
            # 5. LEARN
            old_val = q_table.get(f"{state_key}_{action}", 0)
            next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in config.RED_ACTIONS])
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            
            q_table[f"{state_key}_{action}"] = new_val
            utils.safe_json_write(config.Q_TABLE_RED, q_table)
            
            # 6. TRIGGER ALERTS
            if impact > 0 and random.random() > 0.5:
                war_state['blue_alert_level'] = min(config.MAX_ALERT, current_alert + 1)
                utils.safe_json_write(config.STATE_FILE, war_state)
            
            logger.info(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")
            
            time.sleep(random.uniform(0.5, 1.5))
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Loop error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    engage_offense()
