#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield
"""

import glob
import os
import time
import json
import random
import math
from utils import atomic_json_io, atomic_json_update, atomic_json_merge, calculate_file_entropy

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "blue_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
WATCH_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE"]
ALPHA = 0.4             # Learning Rate (How fast we accept new info)
ALPHA_DECAY = 0.9999    # Stability Factor (Slowly lock in knowledge)
GAMMA = 0.9             # Discount Factor (How much we care about the future)
EPSILON = 0.3           # Exploration Rate (Curiosity)
EPSILON_DECAY = 0.995   # Mastery Curve (Get smarter, less random)
MIN_EPSILON = 0.01      # Always keep 1% curiosity

# --- REWARD CONFIGURATION (AI PERSONALITY) ---
# Tweak these to change how the Defender behaves!
R_MITIGATION = 25       # Reward for killing a threat
R_PATIENCE = 10         # Reward for waiting when safe (saves CPU)
P_WASTE = -15           # Penalty for scanning empty air (Paranoia)
P_NEGLIGENCE = -50      # Penalty for ignoring active malware
MAX_ALERT = 5
MIN_ALERT = 1

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_defense(max_iterations=None):
    global EPSILON, ALPHA
    print(f"{C_CYAN}[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61{C_RESET}")
    
    # Cache Q-Table in memory
    q_table = atomic_json_io(Q_TABLE_FILE)
    steps_since_save = 0
    SAVE_INTERVAL = 10

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1
            try:
                # 1. PREPARATION
                war_state = atomic_json_io(STATE_FILE)
                if not war_state: war_state = {'blue_alert_level': 1}
                # q_table is now cached

                current_alert = war_state.get('blue_alert_level', 1)

                # 2. DETECTION
                visible_threats = glob.glob(os.path.join(WATCH_DIR, 'malware_*'))
                hidden_threats = glob.glob(os.path.join(WATCH_DIR, '.sys_*'))
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
                ALPHA = max(0.1, ALPHA * ALPHA_DECAY) # Stabilize learning over time

                # 4. ERADICATION
                mitigated = 0

                if action == "SIGNATURE_SCAN":
                    for t in visible_threats:
                        try: os.remove(t); mitigated += 1
                        except: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        # Policy: Delete if .sys (Hidden) OR Entropy > 3.5 (Obfuscated)
                        if ".sys" in t or calculate_file_entropy(t) > 3.5:
                            try: os.remove(t); mitigated += 1
                            except: pass

                elif action == "OBSERVE": pass
                elif action == "IGNORE": pass

                # 5. REWARD CALCULATION
                reward = 0
                if mitigated > 0: reward = R_MITIGATION
                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = P_WASTE
                if current_alert >= 4 and action == "OBSERVE": reward = R_PATIENCE
                if action == "IGNORE" and threat_count > 0: reward = P_NEGLIGENCE

                # 6. LEARN
                old_val = q_table.get(f"{state_key}_{action}", 0)
                next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
                new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
                q_table[f"{state_key}_{action}"] = new_val

                # Periodic Persistence
                steps_since_save += 1
                if steps_since_save >= SAVE_INTERVAL:
                    atomic_json_merge(Q_TABLE_FILE, q_table)
                    steps_since_save = 0

                # 7. UPDATE WAR STATE
                should_update = False
                if mitigated > 0 and current_alert < MAX_ALERT:
                    should_update = True
                elif mitigated == 0 and current_alert > MIN_ALERT and action == "OBSERVE":
                    should_update = True

                if should_update:
                    def update_state(state):
                        level = state.get('blue_alert_level', 1)
                        if mitigated > 0 and level < MAX_ALERT:
                            state['blue_alert_level'] = min(MAX_ALERT, level + 1)
                        elif mitigated == 0 and level > MIN_ALERT and action == "OBSERVE":
                            state['blue_alert_level'] = max(MIN_ALERT, level - 1)
                        return state

                    atomic_json_update(STATE_FILE, update_state)

                # LOG
                icon = "🛡️" if mitigated == 0 else "⚔️"
                print(f"{C_BLUE}[BLUE AI]{C_RESET} {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")
                
                time.sleep(0.5 if current_alert >= 4 else 1.0)

            except Exception:
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # Always save on exit
        atomic_json_merge(Q_TABLE_FILE, q_table)

if __name__ == "__main__":
    engage_defense()
