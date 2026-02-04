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
import utils

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "blue_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
SIGNATURE_FILE = os.path.join(BASE_DIR, "signatures.json")
WATCH_DIR = os.environ.get("WAR_ZONE_DIR", "/tmp")

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

# --- DEFENSIVE UTILITIES ---

def calculate_shannon_entropy(filepath):
    """Detects High Entropy (Encrypted/Obfuscated) files."""
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            return utils.calculate_entropy(data)
    except: return 0

MEMORY_CACHE = {}

def access_memory(filepath, data=None):
    """Atomic JSON I/O with read caching."""
    global MEMORY_CACHE

    # WRITE: Always write to disk if data is provided
    if data is not None:
        try:
            with open(filepath, 'w') as f: json.dump(data, f, indent=4)
            # Update cache timestamp to avoid immediate re-read
            if os.path.exists(filepath):
                 MEMORY_CACHE[filepath] = (os.path.getmtime(filepath), data)
        except: pass
        return {}

    # READ: Check modification time
    if os.path.exists(filepath):
        try:
            mtime = os.path.getmtime(filepath)
            if filepath in MEMORY_CACHE:
                cached_mtime, cached_data = MEMORY_CACHE[filepath]
                if mtime == cached_mtime:
                    return cached_data

            # File changed or not in cache, read it
            with open(filepath, 'r') as f:
                data = json.load(f)
                # Validation for state file
                if "war_state.json" in filepath and not utils.validate_state(data):
                    return {}
                MEMORY_CACHE[filepath] = (mtime, data)
                return data
        except: return {}
    return {}

# --- MAIN LOOP ---

def engage_defense():
    global EPSILON, ALPHA
    print(f"{C_CYAN}[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61{C_RESET}")
    
    # Load Q-Table once at startup
    q_table = access_memory(Q_TABLE_FILE)
    if not q_table: q_table = {}

    iteration_count = 0
    SYNC_INTERVAL = 10

    while True:
        try:
            iteration_count += 1

            # 1. PREPARATION
            war_state = access_memory(STATE_FILE)
            if not war_state: war_state = {'blue_alert_level': 1}
            # q_table is now in memory
            
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
                # Check known signatures
                known_sigs = access_memory(SIGNATURE_FILE)
                if not known_sigs: known_sigs = {}

                for t in all_threats: # Now scans all threats against DB
                    try:
                        sz = os.path.getsize(t)
                        if str(sz) in known_sigs:
                            os.remove(t)
                            mitigated += 1
                    except: pass

                # Fallback to simple removal of visible
                for t in visible_threats:
                    if os.path.exists(t):
                        try: os.remove(t); mitigated += 1
                        except: pass
                    
            elif action == "HEURISTIC_SCAN":
                for t in all_threats:
                    # Policy: Delete if .sys (Hidden) OR Entropy > 3.5 (Obfuscated)
                    entropy = calculate_shannon_entropy(t)
                    if ".sys" in t or entropy > 3.5:
                        try:
                            # Learn the signature!
                            sz = os.path.getsize(t)

                            # Atomic update of signatures
                            sigs = access_memory(SIGNATURE_FILE)
                            if not sigs: sigs = {}
                            if str(sz) not in sigs:
                                sigs[str(sz)] = entropy
                                access_memory(SIGNATURE_FILE, sigs)
                                print(f"{C_BLUE}[BLUE LEARNING] Learned signature: Size {sz} | Entropy {entropy:.2f}{C_RESET}")

                            os.remove(t)
                            mitigated += 1
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

            # Sync to disk periodically
            if iteration_count % SYNC_INTERVAL == 0:
                access_memory(Q_TABLE_FILE, q_table)
            
            # 7. UPDATE WAR STATE
            if mitigated > 0 and current_alert < MAX_ALERT:
                war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 1)
            elif mitigated == 0 and current_alert > MIN_ALERT and action == "OBSERVE":
                war_state['blue_alert_level'] = max(MIN_ALERT, current_alert - 1)
                
            access_memory(STATE_FILE, war_state)
            
            # LOG
            icon = "🛡️" if mitigated == 0 else "⚔️"
            print(f"{C_BLUE}[BLUE AI]{C_RESET} {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")
            
            time.sleep(0.5 if current_alert >= 4 else 1.0)

        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    engage_defense()
