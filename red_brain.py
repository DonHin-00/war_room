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
import uuid
from utils import safe_file_read, safe_file_write

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
TARGET_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK", "T1036_MASQUERADE"]
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
def access_memory(filepath, data=None):
    if data is not None:
        try:
            safe_file_write(filepath, json.dumps(data, indent=4))
        except: pass
    if os.path.exists(filepath):
        try:
            content = safe_file_read(filepath)
            return json.loads(content) if content else {}
        except: return {}
    return {}

# --- MAIN LOOP ---

def engage_offense():
    global EPSILON, ALPHA
    print(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
    
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
                fname = os.path.join(TARGET_DIR, f"malware_bait_{uuid.uuid4()}.sh")
                try: 
                    fd = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, 'w') as f: f.write("echo 'scan'")
                    impact = 1
                except: pass
                
            elif action == "T1027_OBFUSCATE":
                # High Entropy Binary
                fname = os.path.join(TARGET_DIR, f"malware_crypt_{uuid.uuid4()}.bin")
                try:
                    fd = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, 'wb') as f: f.write(os.urandom(1024))
                    impact = 3
                except: pass
                
            elif action == "T1003_ROOTKIT":
                # Hidden File
                fname = os.path.join(TARGET_DIR, f".sys_shadow_{uuid.uuid4()}")
                try:
                    fd = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, 'w') as f: f.write("uid=0(root)")
                    impact = 5
                except: pass
                
            elif action == "T1589_LURK":
                impact = 0

            elif action == "T1036_MASQUERADE":
                # Static payload, benign name. Hard to spot, easy to signature.
                fname = os.path.join(TARGET_DIR, f"system_log_{uuid.uuid4()}.txt")
                try:
                    fd = os.open(fname, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                    with os.fdopen(fd, 'wb') as f:
                        # Static malicious payload (Entropy > 3.5 but constant hash)
                        f.write(b"\xde\xad\xbe\xef" * 100 + os.urandom(100))
                        # Note: The os.urandom(100) makes it polymorphic!
                        # Wait, we WANT it to be static to test Blue's learning.
                        # Let's use a fixed seed for the "random" part or just static content.

                    # Overwriting with static content for learning demo
                    with open(fname, 'wb') as f:
                        f.write(b"StaticMaliciousPayload" * 50 + b"\x00\xff" * 50)
                    impact = 2
                except: pass

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
            
            print(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")
            
            time.sleep(random.uniform(0.5, 1.5))
            
        except KeyboardInterrupt:
            break
        except Exception:
            time.sleep(1)

if __name__ == "__main__":
    engage_offense()
