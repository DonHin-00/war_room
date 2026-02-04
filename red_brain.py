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
utils.limit_resources(config.MAX_MEMORY_MB)
logger = utils.setup_logging("RedBrain", config.RED_LOG)
audit = utils.AuditLogger(config.AUDIT_LOG)

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

            # Read Q-Table with Integrity Check
            q_table = utils.safe_json_read(config.Q_TABLE_RED, verify_checksum=True)
            
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
            
            # Resource Check
            if not utils.check_disk_usage(config.SIMULATION_DATA_DIR, config.MAX_DIR_SIZE_MB):
                logger.warning("Target saturated. Halting attack to preserve environment.")
                action = "T1589_LURK" # Force Lurk

            if action == "T1046_RECON":
                # Low Entropy Bait
                fname = os.path.join(config.SIMULATION_DATA_DIR, f"malware_bait_{secrets.token_hex(8)}.sh")
                if utils.secure_create(fname, "echo 'scan'"):
                    impact = 1
                    audit.log_event("RED", "PAYLOAD_DROPPED", {"type": "RECON", "file": fname})
                
            elif action == "T1027_OBFUSCATE":
                # Polymorphism: Mutate payload to change hash
                fname = os.path.join(config.SIMULATION_DATA_DIR, f"malware_crypt_{secrets.token_hex(8)}.bin")
                payload = os.urandom(1024) + secrets.token_bytes(random.randint(16, 64))

                if utils.secure_create(fname, payload, is_binary=True):
                    impact = 3
                    audit.log_event("RED", "PAYLOAD_DROPPED", {"type": "OBFUSCATE", "file": fname})
                
            elif action == "T1003_ROOTKIT":
                # Hidden File
                fname = os.path.join(config.SIMULATION_DATA_DIR, f".sys_shadow_{secrets.token_hex(8)}")
                if utils.secure_create(fname, "uid=0(root)"):
                    impact = 5
                    audit.log_event("RED", "PAYLOAD_DROPPED", {"type": "ROOTKIT", "file": fname})

            elif action == "T1486_ENCRYPT":
                # Ransomware: Find valid file and encrypt it
                targets = [f for f in os.listdir(config.SIMULATION_DATA_DIR)
                           if "malware" not in f and not f.endswith('.enc') and not f.startswith('.sys')]
                if targets:
                    target = random.choice(targets)
                    src = os.path.join(config.SIMULATION_DATA_DIR, target)
                    dst = src + ".enc"
                    try:
                        os.rename(src, dst)
                        impact = 8
                        audit.log_event("RED", "DATA_ENCRYPTED", {"file": target})
                    except Exception: pass

            elif action == "T1589_LURK":
                impact = 0

            # Check for Honeypot interactions (Simulated "Touching" existing files)
            # If Red touches a honeypot, it gets burned.
            existing_files = [f for f in os.listdir(config.SIMULATION_DATA_DIR) if os.path.isfile(os.path.join(config.SIMULATION_DATA_DIR, f))]
            for f in existing_files:
                if f in config.HONEYPOT_NAMES:
                    # Trap Triggered!
                    logger.warning(f"HONEYPOT TRIGGERED: {f}")
                    reward = config.RED_REWARDS['burned']
                    audit.log_event("RED", "TRAP_TRIGGERED", {"file": f})
                    # Reset impact to punish
                    impact = -10
                    break

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
            # Write Q-Table with Integrity Checksum
            utils.safe_json_write(config.Q_TABLE_RED, q_table, write_checksum=True)
            
            # 6. TRIGGER ALERTS
            if impact > 0 and random.random() > 0.5:
                war_state['blue_alert_level'] = min(config.MAX_ALERT, current_alert + 1)
                war_state['timestamp'] = time.time()
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
