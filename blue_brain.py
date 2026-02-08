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

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
Q_TABLE_FILE = os.path.join(BASE_DIR, "blue_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
WATCH_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = [
    "SIGNATURE_SCAN",
    "HEURISTIC_SCAN",
    "OBSERVE",
    "IGNORE",
    "WIFI_DEFENSE",  # New: Counter WiFi attacks
    "WEB_WAF",       # New: Web App Firewall
    "NET_IDS"        # New: Intrusion Detection
]
ALPHA = 0.4             # Learning Rate
ALPHA_DECAY = 0.9999
GAMMA = 0.9
EPSILON = 0.3
EPSILON_DECAY = 0.995
MIN_EPSILON = 0.01

# --- REWARD CONFIGURATION ---
R_MITIGATION = 25
R_PATIENCE = 10
P_WASTE = -15
P_NEGLIGENCE = -50
MAX_ALERT = 5
MIN_ALERT = 1

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

# --- DEFENSIVE UTILITIES ---

def calculate_shannon_entropy(filepath):
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
            if not data: return 0
            entropy = 0
            for x in range(256):
                p_x = float(data.count(x.to_bytes(1, 'little'))) / len(data)
                if p_x > 0:
                    entropy += - p_x * math.log(p_x, 2)
            return entropy
    except: return 0

def access_memory(filepath, data=None):
    if data is not None:
        try:
            with open(filepath, 'w') as f: json.dump(data, f, indent=4)
        except: pass
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f: return json.load(f)
        except: return {}
    return {}

# --- MAIN LOOP ---

def engage_defense():
    global EPSILON, ALPHA
    print(f"{C_CYAN}[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61{C_RESET}")
    print(f"{C_CYAN}[SENTINEL] Sentinel System Updated: Integration with Cyber Muzzle Active{C_RESET}")
    print(f"{C_CYAN}[UPDATE] Capabilities Expanded: WiFi Shield, WAF, IDS online.{C_RESET}")
    
    while True:
        try:
            # 1. PREPARATION
            war_state = access_memory(STATE_FILE)
            if not war_state: war_state = {'blue_alert_level': 1}
            q_table = access_memory(Q_TABLE_FILE)
            
            current_alert = war_state.get('blue_alert_level', 1)
            
            # 2. DETECTION
            visible_threats = glob.glob(os.path.join(WATCH_DIR, 'malware_*'))
            hidden_threats = glob.glob(os.path.join(WATCH_DIR, '.sys_*'))
            
            # Specialized threats
            web_threats = [t for t in visible_threats if t.endswith('.php')]
            wifi_threats = [t for t in visible_threats if 'handshake' in t] # Hypothetical artifact

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
            ALPHA = max(0.1, ALPHA * ALPHA_DECAY)

            # 4. ERADICATION
            mitigated = 0
            
            if action == "SIGNATURE_SCAN":
                for t in visible_threats:
                    if not t.endswith('.php'): # Signature scan might miss new webshells initially? Or catch all basic ones.
                        try: os.remove(t); mitigated += 1
                        except: pass
                    
            elif action == "HEURISTIC_SCAN":
                for t in all_threats:
                    if ".sys" in t or calculate_shannon_entropy(t) > 3.5:
                        try: os.remove(t); mitigated += 1
                        except: pass
            
            elif action == "WEB_WAF":
                for t in web_threats:
                    try: os.remove(t); mitigated += 1
                    except: pass

            elif action == "WIFI_DEFENSE":
                # Simulate preventing handshake capture or deauth
                # For simulation, maybe remove handshake files if they existed
                for t in wifi_threats:
                    try: os.remove(t); mitigated += 1
                    except: pass

            elif action == "NET_IDS":
                # Detect scans (no files to remove usually, but maybe alert)
                if current_alert < MAX_ALERT and threat_count > 0:
                     # Boost alert faster
                     war_state['blue_alert_level'] = min(MAX_ALERT, current_alert + 2)

            elif action == "OBSERVE": pass
            elif action == "IGNORE": pass

            # 5. REWARD CALCULATION
            reward = 0
            if mitigated > 0: reward = R_MITIGATION
            if action == "WEB_WAF" and len(web_threats) > 0: reward += 10 # Bonus for specialized defense
            if action == "HEURISTIC_SCAN" and threat_count == 0: reward = P_WASTE
            if current_alert >= 4 and action == "OBSERVE": reward = R_PATIENCE
            if action == "IGNORE" and threat_count > 0: reward = P_NEGLIGENCE
            
            # 6. LEARN
            old_val = q_table.get(f"{state_key}_{action}", 0)
            next_max = max([q_table.get(f"{state_key}_{a}", 0) for a in ACTIONS])
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            q_table[f"{state_key}_{action}"] = new_val
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
