#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
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
    setup_logging,
    is_honeypot,
    AuditLogger
)
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("RedBrain")
audit = AuditLogger(config.file_paths['audit_log'])

# --- AI HYPERPARAMETERS ---
ACTIONS: List[str] = config.red_actions
ALPHA: float = config.hyperparameters['alpha']
ALPHA_DECAY: float = config.hyperparameters['alpha_decay']
GAMMA: float = config.hyperparameters['gamma']
EPSILON: float = config.hyperparameters['epsilon']
EPSILON_DECAY: float = config.hyperparameters['epsilon_decay']
MIN_EPSILON: float = config.hyperparameters['min_epsilon']

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_offense(max_iterations: Optional[int] = None) -> None:
    global EPSILON, ALPHA

    msg = f"[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE"
    print(f"{C_RED}{msg}{C_RESET}")
    logger.info(msg)

    q_table_path = config.file_paths['red_q_table']
    q_table: Dict[str, float] = atomic_json_io(q_table_path)

    steps_since_save = 0
    save_interval = config.constraints['save_interval']
    target_dir = config.file_paths['watch_dir']
    state_file = config.file_paths['state_file']

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1
            try:
                # 1. RECON
                war_state: Dict[str, Any] = atomic_json_io(state_file)
                if not war_state: war_state = {'blue_alert_level': 1}

                current_alert = war_state.get('blue_alert_level', 1)
                state_key = f"{current_alert}"

                # LOW AND SLOW: If alert is high, sleep more
                if current_alert >= 4:
                    time.sleep(random.uniform(2.0, 5.0))

                # 2. STRATEGY
                action: str = ""
                if random.random() < EPSILON:
                    action = random.choice(ACTIONS)
                else:
                    action = max(ACTIONS, key=lambda a: q_table.get(f"{state_key}_{a}", 0.0))

                EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
                ALPHA = max(0.1, ALPHA * ALPHA_DECAY)

                # 3. EXECUTION
                impact = 0
                burned = False

                # Check for honeypots before acting? (Smart Red)
                # For now, simplistic interaction

                if action == "T1046_RECON":
                    # Check if any honeypots exist
                    try:
                        with os.scandir(target_dir) as it:
                            for entry in it:
                                if is_honeypot(entry.path):
                                    burned = True
                                    audit.log("RED", "TRIPPED_HONEYPOT", {"file": entry.name})
                                    break
                    except: pass

                    if not burned:
                        fname = os.path.join(target_dir, f"malware_bait_{int(time.time())}.sh")
                        try:
                            with open(fname, 'w') as f: f.write("echo 'scan'")
                            impact = 1
                        except: pass

                elif action == "T1027_OBFUSCATE":
                    # POLYMORPHISM: Append random junk to change entropy/hash
                    fname = os.path.join(target_dir, f"malware_crypt_{int(time.time())}.bin")
                    try:
                        payload = os.urandom(1024)
                        padding = os.urandom(random.randint(100, 500)) # Polymorphic padding
                        with open(fname, 'wb') as f: f.write(payload + padding)
                        impact = 3
                    except: pass

                elif action == "T1003_ROOTKIT":
                    fname = os.path.join(target_dir, f".sys_shadow_{int(time.time())}")
                    try:
                        with open(fname, 'w') as f: f.write("uid=0(root)")
                        impact = 5
                    except: pass

                elif action == "T1589_LURK":
                    impact = 0

                # 4. REWARDS
                reward = 0
                max_alert = config.constraints['max_alert']
                if impact > 0:
                    reward = config.red_rewards['impact']
                if current_alert >= 4 and action == "T1589_LURK":
                    reward = config.red_rewards['stealth']
                if current_alert == max_alert and impact > 0:
                    reward = config.red_rewards['critical']
                if burned:
                    reward = config.red_rewards['burned'] # Huge penalty

                # 5. LEARN
                old_val = q_table.get(f"{state_key}_{action}", 0.0)
                next_max = max(q_table.get(f"{state_key}_{a}", 0.0) for a in ACTIONS)
                new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
                q_table[f"{state_key}_{action}"] = new_val

                # Periodic Persistence
                steps_since_save += 1
                if steps_since_save >= save_interval:
                    atomic_json_merge(q_table_path, q_table)
                    steps_since_save = 0

                # 6. TRIGGER ALERTS
                if impact > 0 and random.random() > 0.5:
                    def update_state(state):
                        state['blue_alert_level'] = min(max_alert, state.get('blue_alert_level', 1) + 1)
                        return state
                    atomic_json_update(state_file, update_state)

                if impact > 0:
                    audit.log("RED", "ATTACK_LAUNCHED", {"technique": action, "impact": impact})

                log_msg = f"👹 State: {state_key} | Tech: {action} | Impact: {impact} | Burned: {burned} | Q: {new_val:.2f}"
                print(f"{C_RED}[RED AI] {C_RESET} {log_msg}")
                logger.info(log_msg)

                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        atomic_json_merge(q_table_path, q_table)
        logger.info("Red Team AI Shutting Down")

if __name__ == "__main__":
    engage_offense()
