#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield
"""

import os
import sys
import time
import random
import logging
from typing import Optional, List, Dict, Any

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    atomic_json_io,
    atomic_json_update,
    atomic_json_merge,
    calculate_file_entropy,
    setup_logging,
    is_honeypot,
    AuditLogger
)
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("BlueBrain")
audit = AuditLogger(config.file_paths['audit_log'])

# --- AI HYPERPARAMETERS ---
ACTIONS: List[str] = config.blue_actions
ALPHA: float = config.hyperparameters['alpha']
ALPHA_DECAY: float = config.hyperparameters['alpha_decay']
GAMMA: float = config.hyperparameters['gamma']
EPSILON: float = config.hyperparameters['epsilon']
EPSILON_DECAY: float = config.hyperparameters['epsilon_decay']
MIN_EPSILON: float = config.hyperparameters['min_epsilon']

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_defense(max_iterations: Optional[int] = None) -> None:
    global EPSILON, ALPHA

    msg = f"[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61"
    print(f"{C_CYAN}{msg}{C_RESET}")
    logger.info(msg)

    # Cache Q-Table in memory
    q_table_path = config.file_paths['blue_q_table']
    q_table: Dict[str, float] = atomic_json_io(q_table_path)

    steps_since_save = 0
    save_interval = config.constraints['save_interval']
    watch_dir = config.file_paths['watch_dir']
    state_file = config.file_paths['state_file']

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1
            try:
                # 1. PREPARATION
                war_state: Dict[str, Any] = atomic_json_io(state_file)
                if not war_state: war_state = {'blue_alert_level': 1}

                current_alert = war_state.get('blue_alert_level', 1)

                # 2. DETECTION
                visible_threats: List[str] = []
                hidden_threats: List[str] = []
                # Scan for honeypots first - did Red touch them?
                # (Simplification: If honeypot missing/modified, assume Red)
                # For this sim, we just check existence. Real logic would track file hashes.

                try:
                    with os.scandir(watch_dir) as it:
                        for entry in it:
                            if entry.is_file():
                                if entry.name.startswith('malware_'):
                                    visible_threats.append(entry.path)
                                elif entry.name.startswith('.sys_'):
                                    hidden_threats.append(entry.path)
                except FileNotFoundError:
                    pass

                all_threats = visible_threats + hidden_threats
                threat_count = len(all_threats)
                state_key = f"{current_alert}_{threat_count}"

                # 3. DECISION
                action: str = ""
                if random.random() < EPSILON:
                    action = random.choice(ACTIONS)
                else:
                    action = max(ACTIONS, key=lambda a: q_table.get(f"{state_key}_{a}", 0.0))

                EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
                ALPHA = max(0.1, ALPHA * ALPHA_DECAY)

                # 4. ERADICATION / DECEPTION
                mitigated = 0
                trapped = 0

                if action == "SIGNATURE_SCAN":
                    for t in visible_threats:
                        if not is_honeypot(t):
                            try: os.remove(t); mitigated += 1
                            except: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        if not is_honeypot(t):
                            if ".sys" in t or calculate_file_entropy(t) > 3.5:
                                try: os.remove(t); mitigated += 1
                                except: pass

                elif action == "DEPLOY_DECOY":
                    # Plant a honeypot
                    hp_name = random.choice(config.HONEYPOT_NAMES)
                    hp_path = os.path.join(watch_dir, hp_name)
                    if not os.path.exists(hp_path):
                        try:
                            with open(hp_path, 'w') as f: f.write("SUPER SECRET PASSWORD = admin123")
                            trapped = 1 # Metaphorical success
                            audit.log("BLUE", "HONEYPOT_DEPLOYED", {"file": hp_name})
                        except: pass

                elif action == "OBSERVE": pass
                elif action == "IGNORE": pass

                # 5. REWARD CALCULATION
                reward = 0
                if mitigated > 0:
                    reward = config.blue_rewards['mitigation']
                if action == "HEURISTIC_SCAN" and threat_count == 0:
                    reward = config.blue_rewards['waste']
                if current_alert >= 4 and action == "OBSERVE":
                    reward = config.blue_rewards['patience']
                if action == "IGNORE" and threat_count > 0:
                    reward = config.blue_rewards['negligence']
                if trapped > 0:
                    reward = 5 # Small reward for deploying defense

                # 6. LEARN
                old_val = q_table.get(f"{state_key}_{action}", 0.0)
                next_max = max(q_table.get(f"{state_key}_{a}", 0.0) for a in ACTIONS)
                new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
                q_table[f"{state_key}_{action}"] = new_val

                # Periodic Persistence
                steps_since_save += 1
                if steps_since_save >= save_interval:
                    atomic_json_merge(q_table_path, q_table)
                    steps_since_save = 0

                # 7. UPDATE WAR STATE
                should_update = False
                max_alert = config.constraints['max_alert']
                min_alert = config.constraints['min_alert']

                if mitigated > 0 and current_alert < max_alert:
                    should_update = True
                elif mitigated == 0 and current_alert > min_alert and action == "OBSERVE":
                    should_update = True

                if should_update:
                    def update_state(state):
                        level = state.get('blue_alert_level', 1)
                        if mitigated > 0 and level < max_alert:
                            state['blue_alert_level'] = min(max_alert, level + 1)
                        elif mitigated == 0 and level > min_alert and action == "OBSERVE":
                            state['blue_alert_level'] = max(min_alert, level - 1)
                        return state

                    atomic_json_update(state_file, update_state)

                if mitigated > 0 or trapped > 0:
                    audit.log("BLUE", "ACTION_TAKEN", {"action": action, "mitigated": mitigated})

                # LOG
                icon = "🛡️" if mitigated == 0 else "⚔️"
                log_msg = f"{icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}"
                print(f"{C_BLUE}[BLUE AI]{C_RESET} {log_msg}")
                logger.info(log_msg)

                time.sleep(0.5 if current_alert >= 4 else 1.0)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        atomic_json_merge(q_table_path, q_table)
        logger.info("Blue Team AI Shutting Down")

if __name__ == "__main__":
    engage_defense()
