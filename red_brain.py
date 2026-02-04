#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import json
import random
import logging
import secrets

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("RedBrain")

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
TARGET_DIR = os.path.join(BASE_DIR, "simulation_data")

# Ensure secure directory exists
if not os.path.exists(TARGET_DIR):
    os.makedirs(TARGET_DIR, mode=0o700)

# --- AI HYPERPARAMETERS ---
ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK"]
ALPHA = 0.4
ALPHA_DECAY = 0.9999
GAMMA = 0.9
EPSILON = 0.3
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01

# --- REWARD CONFIGURATION (ATTACKER PROFILE) ---
R_IMPACT = 10           # Base points for successful drop
R_STEALTH = 15          # Points for lurking when heat is high
R_CRITICAL = 30         # Bonus for attacking during Max Alert (Brazen)
MAX_ALERT = 5

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

# --- UTILITIES ---
def secure_create(filepath, content, is_binary=False):
    """Securely create a file, failing if it exists (Atomic)."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    mode = 0o600
    try:
        fd = os.open(filepath, flags, mode)
        with os.fdopen(fd, 'wb' if is_binary else 'w') as f:
            f.write(content)
        return True
    except OSError:
        return False

def access_memory(filepath, data=None):
    if data is not None:
        try:
            with open(filepath, 'w') as f: json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Memory write failed {filepath}: {e}")
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f: return json.load(f)
        except Exception as e:
            logger.error(f"Memory read failed {filepath}: {e}")
            return {}
    return {}

# --- MAIN LOOP ---

def engage_offense():
    global EPSILON, ALPHA
    logger.info(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
    
    while True:
        try:
            # 1. RECON
            war_state = access_memory(STATE_FILE)
            if not war_state: war_state = {'blue_alert_level': 1}
            q_table = access_memory(Q_TABLE_FILE)
            
            current_alert = war_state.get('blue_alert_level', 1)
            state_key = f"{current_alert}"
            
            # 2. STRATEGY
            if random.random() < EPSILON:
                action = random.choice(ACTIONS)
            else:
                known = {a: q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS}
                action = max(known, key=known.get)
                
            EPSILON = max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
            ALPHA = max(0.1, ALPHA * ALPHA_DECAY)

            # 3. EXECUTION
            impact = 0
            
            if action == "T1046_RECON":
                # Low Entropy Bait
                fname = os.path.join(TARGET_DIR, f"malware_bait_{secrets.token_hex(8)}.sh")
                if secure_create(fname, "echo 'scan'"):
                    impact = 1
                
            elif action == "T1027_OBFUSCATE":
                # High Entropy Binary
                fname = os.path.join(TARGET_DIR, f"malware_crypt_{secrets.token_hex(8)}.bin")
                if secure_create(fname, os.urandom(1024), is_binary=True):
                    impact = 3
                
            elif action == "T1003_ROOTKIT":
                # Hidden File
                fname = os.path.join(TARGET_DIR, f".sys_shadow_{secrets.token_hex(8)}")
                if secure_create(fname, "uid=0(root)"):
                    impact = 5
                
            elif action == "T1589_LURK":
                impact = 0

            # 4. REWARDS
            reward = 0
            if impact > 0: reward = R_IMPACT
            if current_alert >= 4 and action == "T1589_LURK": reward = R_STEALTH
            if current_alert == MAX_ALERT and impact > 0: reward = R_CRITICAL
            
            # 5. LEARN
            old_val = q_table.get(f"{state_key}_{action}", 0)
            next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            
            q_table[f"{state_key}_{action}"] = new_val
            access_memory(Q_TABLE_FILE, q_table)
            
            # 6. TRIGGER ALERTS
            if impact > 0 and random.random() > 0.5:
                war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 1)
                access_memory(STATE_FILE, war_state)
            
            logger.info(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")
            
            time.sleep(random.uniform(0.5, 1.5))
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error(f"Loop error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    engage_offense()
