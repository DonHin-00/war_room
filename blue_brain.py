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

# --- SYSTEM INITIALIZATION ---
utils.check_root()
logger = utils.setup_logging("BlueBrain", config.BLUE_LOG)

# --- AI STATE ---
# We use config hyperparameters
ALPHA = config.HYPERPARAMETERS['learning_rate']
ALPHA_DECAY = config.HYPERPARAMETERS['learning_rate_decay']
GAMMA = config.HYPERPARAMETERS['discount_factor']
EPSILON = config.HYPERPARAMETERS['epsilon']
EPSILON_DECAY = config.HYPERPARAMETERS['epsilon_decay']
MIN_EPSILON = config.HYPERPARAMETERS['min_epsilon']

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_defense():
    global EPSILON, ALPHA
    logger.info(f"{C_CYAN}[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61{C_RESET}")
    
    while True:
        try:
            # 1. PREPARATION
            war_state = utils.safe_json_read(config.STATE_FILE, {'blue_alert_level': 1})
            # Input Validation
            if not utils.validate_state(war_state):
                logger.warning("Corrupted state detected, resetting.")
                war_state = {'blue_alert_level': 1}

            # Read Q-Table with Integrity Check
            q_table = utils.safe_json_read(config.Q_TABLE_BLUE, verify_checksum=True)
            
            current_alert = war_state.get('blue_alert_level', 1)
            
            # 2. DETECTION
            # Resource Protection (Anti-DoS)
            if not utils.check_disk_usage(config.SIMULATION_DATA_DIR, config.MAX_DIR_SIZE_MB):
                logger.critical("DISK QUOTA EXCEEDED! Initiating Emergency Purge.")
                # Emergency Purge
                files = glob.glob(os.path.join(config.SIMULATION_DATA_DIR, '*'))
                for f in files:
                    try:
                        if not os.path.islink(f): os.remove(f)
                    except Exception: pass
                # Reset threats list after purge
                visible_threats = []
                hidden_threats = []
            else:
                visible_threats = glob.glob(os.path.join(config.SIMULATION_DATA_DIR, 'malware_*'))
                hidden_threats = glob.glob(os.path.join(config.SIMULATION_DATA_DIR, '.sys_*'))

            all_threats = visible_threats + hidden_threats
            
            threat_count = len(all_threats)
            state_key = f"{current_alert}_{threat_count}"
            
            # 3. DECISION
            if random.random() < EPSILON:
                action = random.choice(config.BLUE_ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in config.BLUE_ACTIONS}
                action = max(known, key=known.get)
            
            EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
            ALPHA = max(0.1, ALPHA * ALPHA_DECAY) # Stabilize learning over time

            # 4. ERADICATION
            mitigated = 0
            
            if action == "SIGNATURE_SCAN":
                for t in visible_threats:
                    # Security: Prevent symlink attacks
                    if os.path.islink(t):
                        try:
                            os.remove(t)
                            mitigated += 1
                        except OSError as e:
                            logger.error(f"Failed to remove symlink {t}: {e}")
                        continue

                    try:
                        os.remove(t)
                        mitigated += 1
                    except OSError as e:
                        logger.error(f"Failed to remove file {t}: {e}")
                    
            elif action == "HEURISTIC_SCAN":
                for t in all_threats:
                    # Security: Prevent symlink attacks (don't read target)
                    if os.path.islink(t):
                        try:
                            os.remove(t)
                            mitigated += 1
                        except OSError as e:
                            logger.error(f"Failed to remove symlink {t}: {e}")
                        continue

                    # Policy: Delete if .sys (Hidden) OR Entropy > 3.5 (Obfuscated)
                    # Using utils.calculate_entropy
                    try:
                        with open(t, 'rb') as f:
                            content = f.read()
                        entropy = utils.calculate_entropy(content)
                    except Exception:
                        entropy = 0

                    if ".sys" in t or entropy > 3.5:
                        try:
                            os.remove(t)
                            mitigated += 1
                        except OSError as e:
                            logger.error(f"Failed to remove suspect {t}: {e}")
            
            elif action == "OBSERVE": pass
            elif action == "IGNORE": pass

            # 5. REWARD CALCULATION
            reward = 0
            if mitigated > 0: reward = config.BLUE_REWARDS['mitigation']
            if action == "HEURISTIC_SCAN" and threat_count == 0: reward = config.BLUE_REWARDS['waste']
            if current_alert >= 4 and action == "OBSERVE": reward = config.BLUE_REWARDS['patience']
            if action == "IGNORE" and threat_count > 0: reward = config.BLUE_REWARDS['negligence']
            
            # 6. LEARN
            old_val = q_table.get(f"{state_key}_{action}", 0)
            next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in config.BLUE_ACTIONS])
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            q_table[f"{state_key}_{action}"] = new_val
            # Write Q-Table with Integrity Checksum
            utils.safe_json_write(config.Q_TABLE_BLUE, q_table, write_checksum=True)
            
            # 7. UPDATE WAR STATE
            state_changed = False
            if mitigated > 0 and current_alert < config.MAX_ALERT:
                war_state['blue_alert_level'] = min(config.MAX_ALERT, current_alert + 1)
                state_changed = True
            elif mitigated == 0 and current_alert > config.MIN_ALERT and action == "OBSERVE":
                war_state['blue_alert_level'] = max(config.MIN_ALERT, current_alert - 1)
                state_changed = True
                
            if state_changed:
                war_state['timestamp'] = time.time()
                utils.safe_json_write(config.STATE_FILE, war_state)
            
            # LOG
            icon = "🛡️" if mitigated == 0 else "⚔️"
            logger.info(f"{C_BLUE}[BLUE AI]{C_RESET} {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")
            
            time.sleep(0.5 if current_alert >= 4 else 1.0)

        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"System Loop Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    engage_defense()
