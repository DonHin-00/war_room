#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import random
import utils

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Q_TABLE_FILE removed
THREAT_DB_FILE = os.path.join(BASE_DIR, "threat_db.json")
TARGET_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK", "T1036_MASQUERADE", "T1486_ENCRYPT", "T1070_CLEANUP"]
ALPHA = 0.4
ALPHA_DECAY = 0.9999
GAMMA = 0.9
EPSILON = 0.3
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01
SYNC_INTERVAL = 10      # How often to save Q-Table to disk
R_IMPACT = 10           # Base points for successful drop
R_STEALTH = 15          # Points for lurking when heat is high
R_CRITICAL = 30         # Bonus for attacking during Max Alert (Brazen)
MAX_ALERT = 5

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_offense():
    global EPSILON, ALPHA
    print(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
    
    # Load Q-Table (SQLite)
    q_manager = utils.QTableManager("red", ACTIONS)

    threat_loader = utils.SmartJSONLoader(THREAT_DB_FILE, {'hashes': [], 'filenames': []})
    step_count = 0

    # Local optimizations
    _random = random.random
    _choice = random.choice
    _sleep = time.sleep
    _max = max
    _time = time.time

    while True:
        try:
            step_count += 1
            
            # 1. RECON
            current_alert = utils.DB.get_state("blue_alert_level", 1)
            state_key = f"{current_alert}"
            
            # 2. STRATEGY
            if _random() < EPSILON:
                action = _choice(ACTIONS)
            else:
                action = q_manager.get_best_action(state_key)
                
            EPSILON = _max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
            ALPHA = _max(0.1, ALPHA * ALPHA_DECAY)

            # 3. EXECUTION
            impact = 0
            timestamp = int(_time())

            # Optimization: Pre-calculate paths outside conditional logic if possible,
            # but here filenames depend on action. We can optimize string formatting though.
            
            if action == "T1046_RECON":
                # Low Entropy Bait
                fname = f"{TARGET_DIR}/malware_bait_{timestamp}.sh"
                try: 
                    with open(fname, 'w') as f: f.write("echo 'scan'")
                    impact = 1
                except: pass
                
            elif action == "T1027_OBFUSCATE":
                # High Entropy Binary
                fname = f"{TARGET_DIR}/malware_crypt_{timestamp}.bin"
                try:
                    with open(fname, 'wb') as f: f.write(os.urandom(1024))
                    impact = 3
                except: pass
                
            elif action == "T1003_ROOTKIT":
                # Hidden File
                fname = f"{TARGET_DIR}/.sys_shadow_{timestamp}"
                try:
                    with open(fname, 'w') as f: f.write("uid=0(root)")
                    impact = 5
                except: pass

            elif action == "T1036_MASQUERADE":
                # Use real malware name from intel feed
                threat_intel, _ = threat_loader.load()
                names = threat_intel.get('filenames', [])

                if names:
                    # Smart Masquerade: Try to match extension context if possible,
                    # but for now just pick a random real malware name to confuse Blue
                    fake_name = _choice(names)
                    fake_name = os.path.basename(fake_name)

                    # Ensure it has an extension, otherwise it looks suspicious if we just drop "malware"
                    if '.' not in fake_name:
                        fake_name += ".exe"

                    fname = f"{TARGET_DIR}/{fake_name}"
                    try:
                        # Write random content to match the "file type" roughly in size?
                        # No, just standard payload for now.
                        with open(fname, 'w') as f: f.write("real_sample_simulation_payload")
                        impact = 4
                    except: pass
                else:
                    # Fallback if no internet/feed data
                    fname = f"{TARGET_DIR}/svchost.exe"
                    try:
                        with open(fname, 'w') as f: f.write("fake_service")
                        impact = 2
                    except: pass
                
            elif action == "T1589_LURK":
                impact = 0

            elif action == "T1486_ENCRYPT":
                # Ransomware Simulation: Encrypt a file (rename to .enc)
                try:
                    files = [f.path for f in os.scandir(TARGET_DIR) if f.is_file() and not f.name.endswith('.enc')]
                    if files:
                        target = _choice(files)
                        new_name = target + ".enc"
                        os.rename(target, new_name)
                        impact = 8
                except: pass

            elif action == "T1070_CLEANUP":
                # Anti-forensics: Delete logs or self
                try:
                    # Delete self-dropped scripts
                    files = [f.path for f in os.scandir(TARGET_DIR) if f.name.startswith('malware_')]
                    if files:
                        target = _choice(files)
                        os.remove(target)
                        impact = 2 # Low impact but good for evasion
                except: pass

            # 4. REWARDS
            reward = 0
            if impact > 0: reward = R_IMPACT
            if current_alert >= 4 and action == "T1589_LURK": reward = R_STEALTH
            if current_alert == MAX_ALERT and impact > 0: reward = R_CRITICAL
            
            # 5. LEARN
            old_val = q_manager.get_q(state_key, action)
            next_max = q_manager.get_max_q(state_key)
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            
            q_manager.update_q(state_key, action, new_val)

            # Sync Q-Table periodically (Implicitly handled by SQLite WAL)
            pass
            
            # 6. TRIGGER ALERTS
            if impact > 0 and _random() > 0.5:
                utils.DB.set_state("blue_alert_level", min(MAX_ALERT, current_alert + 1))
            
            print(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")
            
            # Adaptive sleep based on impact
            activity = 1.0 if impact > 0 else 0.0
            utils.adaptive_sleep(1.0, activity)
            
        except KeyboardInterrupt:
            break
        except Exception:
            _sleep(1)

if __name__ == "__main__":
    engage_offense()
