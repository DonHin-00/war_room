#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield
"""

import os
import time
import random
import utils
import drone_network

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Q_TABLE_FILE removed (Moved to SQLite)
STATE_FILE = os.path.join(BASE_DIR, "war_state.json") # Keep for compat or migrate? Migrate state too.
THREAT_DB_FILE = os.path.join(BASE_DIR, "threat_db.json")
WATCH_DIR = "/tmp"

# --- AI HYPERPARAMETERS ---
ACTIONS = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE", "DEPLOY_DRONES", "BACKUP_RESTORE"]
ALPHA = 0.4             # Learning Rate (How fast we accept new info)
ALPHA_DECAY = 0.9999    # Stability Factor (Slowly lock in knowledge)
GAMMA = 0.9             # Discount Factor (How much we care about the future)
EPSILON = 0.3           # Exploration Rate (Curiosity)
EPSILON_DECAY = 0.995   # Mastery Curve (Get smarter, less random)
MIN_EPSILON = 0.01      # Always keep 1% curiosity
SYNC_INTERVAL = 10      # How often to save Q-Table to disk

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

# --- MAIN LOOP ---

def engage_defense():
    global EPSILON, ALPHA
    print(f"{C_CYAN}[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61{C_RESET}")
    
    # Load Q-Table (SQLite)
    q_manager = utils.QTableManager("blue", ACTIONS)

    # Drones
    swarm = drone_network.DroneSwarm(4, WATCH_DIR)

    # State loaders (Legacy file support + DB)
    threat_loader = utils.SmartJSONLoader(THREAT_DB_FILE, {'hashes': [], 'filenames': []})
    file_cache = utils.FileIntegrityCache()
    step_count = 0

    # Local optimizations
    _random = random.random
    _choice = random.choice
    _sleep = time.sleep
    _max = max

    while True:
        try:
            step_count += 1

            # 1. PREPARATION
            # Use DB for state, fallback to file if needed (or just use DB exclusively)
            # For now, let's read from DB primarily
            current_alert = utils.DB.get_state("blue_alert_level", 1)
            
            # 2. DETECTION
            # Optimization: avoid creating 'all_threats' list via concatenation
            visible_threats, hidden_threats = utils.scan_threats(WATCH_DIR)
            threat_count = len(visible_threats) + len(hidden_threats)
            state_key = f"{current_alert}_{threat_count}"
            
            # 3. DECISION
            if _random() < EPSILON:
                action = _choice(ACTIONS)
            else:
                action = q_manager.get_best_action(state_key)
            
            EPSILON = _max(MIN_EPSILON, EPSILON * EPSILON_DECAY)
            ALPHA = _max(0.1, ALPHA * ALPHA_DECAY) # Stabilize learning over time

            # 4. ERADICATION
            mitigated = 0
            
            if action == "SIGNATURE_SCAN":
                # Real Intel Scan
                threat_intel, _ = threat_loader.load()
                known_hashes = set(threat_intel.get('hashes', []))
                known_names = set(threat_intel.get('filenames', []))

                for t in visible_threats:
                    try:
                        # Check 1: Filename Blocklist (Fastest)
                        fname = os.path.basename(t)
                        if fname in known_names:
                            print(f"{C_CYAN}[BLOCK] Signature Match (Filename): {fname}{C_RESET}")
                            os.remove(t)
                            mitigated += 1
                            continue

                        # Check 2: Hash Blocklist (Slower, requires read)
                        # Only hash if we have hashes to check against (save CPU)
                        if known_hashes:
                             f_hash = utils.calculate_sha256(t)
                             if f_hash in known_hashes:
                                 print(f"{C_CYAN}[BLOCK] Signature Match (SHA256): {f_hash[:8]}...{C_RESET}")
                                 os.remove(t)
                                 mitigated += 1
                                 continue

                        # Fallback: Default cleanup (if allowed by policy, otherwise wait for Heuristic)
                        # Actually, SIGNATURE_SCAN usually implies we know it's bad.
                        # But in this sim, visible_threats are 'malware_*' so they are bad by definition.
                        os.remove(t); mitigated += 1
                    except: pass
                    
            elif action == "HEURISTIC_SCAN":
                # Optimization: Iterate over lists directly, avoiding 'all_threats' creation
                # Chain iteration would be cleaner but simple loops are fast enough here
                for t in hidden_threats:
                    try: os.remove(t); mitigated += 1
                    except: pass

                # Only analyze NEW or MODIFIED visible files for entropy
                # This changes complexity from O(N) to O(Delta)
                changed_visible = file_cache.filter_changed(visible_threats)

                for t in changed_visible:
                     # Only check entropy for visible files (hidden are deleted by policy above)
                    if calculate_shannon_entropy(t) > 3.5:
                        try:
                            os.remove(t)
                            mitigated += 1
                            file_cache.invalidate(t) # Remove from cache
                        except: pass
            
            elif action == "OBSERVE": pass
            elif action == "IGNORE": pass

            elif action == "DEPLOY_DRONES":
                swarm.activate()
                # Drones might update DB state if they find something
                mitigated += 1 # Small reward for activity

            elif action == "BACKUP_RESTORE":
                # Restore encrypted files (simulate backup recovery)
                try:
                    encrypted = [f for f in visible_threats if f.endswith('.enc')]
                    for enc_file in encrypted:
                        # Restore: remove .enc extension
                        orig_name = enc_file[:-4]
                        os.rename(enc_file, orig_name)
                        mitigated += 2 # High reward for recovery
                except: pass

            # 5. REWARD CALCULATION
            reward = 0
            if mitigated > 0: reward = R_MITIGATION
            if action == "HEURISTIC_SCAN" and threat_count == 0: reward = P_WASTE
            if current_alert >= 4 and action == "OBSERVE": reward = R_PATIENCE
            if action == "IGNORE" and threat_count > 0: reward = P_NEGLIGENCE
            
            # 6. LEARN
            old_val = q_manager.get_q(state_key, action)
            next_max = q_manager.get_max_q(state_key)
            new_val = old_val + ALPHA * (reward + GAMMA * next_max - old_val)
            q_manager.update_q(state_key, action, new_val)

            # Sync Q-Table periodically (Implicitly handled by SQLite WAL, but we can do nothing here)
            # Learn from Proxy War Experience (Transfer Learning)
            if step_count % 50 == 0:
                learned = q_manager.learn_from_replay(batch_size=20, alpha=ALPHA, gamma=GAMMA)
                if learned > 0:
                    print(f"{C_CYAN}[BLUE] Learned from {learned} Proxy scenarios{C_RESET}")
            
            # 7. UPDATE WAR STATE
            if mitigated > 0 and current_alert < MAX_ALERT:
                utils.DB.set_state("blue_alert_level", min(MAX_ALERT, current_alert + 1))
            elif mitigated == 0 and current_alert > MIN_ALERT and action == "OBSERVE":
                utils.DB.set_state("blue_alert_level", max(MIN_ALERT, current_alert - 1))
            
            # LOG
            icon = "🛡️" if mitigated == 0 else "⚔️"
            print(f"{C_BLUE}[BLUE AI]{C_RESET} {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")
            
            # Adaptive sleep based on threat level
            activity = 1.0 if current_alert >= 4 else 0.0
            utils.adaptive_sleep(1.0, activity)

        except KeyboardInterrupt:
            break
        except Exception:
            _sleep(1)

if __name__ == "__main__":
    engage_defense()
