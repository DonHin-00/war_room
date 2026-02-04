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
utils.limit_resources(config.MAX_MEMORY_MB)
logger = utils.setup_logging("BlueBrain", config.BLUE_LOG)
audit = utils.AuditLogger(config.AUDIT_LOG)

# Zero Trust Login
id_mgr = utils.IdentityManager(config.SESSION_DB)
SESSION_TOKEN = id_mgr.login("BlueBrain")
logger.info(f"Authenticated with Kernel. Session Active.")

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

            # Load Signatures
            signatures = utils.safe_json_read(config.SIGNATURE_DB, [])
            
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
                    if os.path.islink(t): continue

                    # Check against Signature DB
                    try:
                        with open(t, 'rb') as f: content = f.read()
                        file_hash = utils.calculate_checksum(content.decode('latin1')) # Hacky decode for binary

                        if file_hash in signatures:
                            os.remove(t)
                            mitigated += 1
                            audit.log_event("BLUE", "SIGNATURE_MATCH", {"file": t, "hash": file_hash})
                    except Exception as e:
                        # Fallback to blind delete if it looks like malware but fails read?
                        # No, strict signature match means we only kill what we know.
                        pass
                    
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

                    # Ignore own honeypots
                    if os.path.basename(t) in config.HONEYPOT_NAMES:
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
                            # Learning: Add to Signatures
                            with open(t, 'rb') as f: content = f.read()
                            file_hash = utils.calculate_checksum(content.decode('latin1'))
                            if file_hash not in signatures:
                                signatures.append(file_hash)
                                utils.safe_json_write(config.SIGNATURE_DB, signatures)
                                audit.log_event("BLUE", "NEW_SIGNATURE_LEARNED", {"hash": file_hash})

                            os.remove(t)
                            mitigated += 1
                            audit.log_event("BLUE", "THREAT_ELIMINATED", {"file": t, "entropy": entropy})
                        except OSError as e:
                            logger.error(f"Failed to remove suspect {t}: {e}")

            elif action == "DEPLOY_DECEPTION":
                # Deploy Honeypots
                for name in config.HONEYPOT_NAMES:
                    target = os.path.join(config.SIMULATION_DATA_DIR, name)
                    if not os.path.exists(target):
                        # Use a realistic looking bait (random binary or text)
                        utils.secure_create(target, f"REAL DATA: {random.randint(1000,9999)}", token=SESSION_TOKEN)
                        audit.log_event("BLUE", "HONEYPOT_DEPLOYED", {"file": name})

            elif action == "BACKUP_CRITICAL":
                # Backup any non-malicious files
                valid_files = [f for f in glob.glob(os.path.join(config.SIMULATION_DATA_DIR, '*'))
                               if "malware" not in f and ".sys" not in f and not f.endswith('.enc')]
                for f in valid_files:
                    if utils.secure_backup(f, config.BACKUP_DIR):
                        audit.log_event("BLUE", "DATA_BACKUP", {"file": f})

                # Check for Ransomware (.enc) and Restore
                encrypted_files = glob.glob(os.path.join(config.SIMULATION_DATA_DIR, '*.enc'))
                for f in encrypted_files:
                    original_name = os.path.basename(f).replace('.enc', '')
                    if utils.secure_restore(original_name, config.BACKUP_DIR, config.SIMULATION_DATA_DIR):
                        os.remove(f) # Remove encrypted copy
                        mitigated += 2 # Big win for recovery
                        audit.log_event("BLUE", "RANSOMWARE_RECOVERY", {"file": original_name})

            elif action == "NETWORK_FILTER":
                # Network Traffic Analysis (NTA)
                packets = glob.glob(os.path.join(config.NETWORK_BUS_DIR, 'packet_*.dat'))
                for p in packets:
                    try:
                        if os.path.islink(p): continue
                        with open(p, 'r') as f: content = f.read()

                        # Simulated Firewall Rule: Block Base64 C2
                        import base64
                        try:
                            decoded = base64.b64decode(content).decode()
                            if "HEARTBEAT" in decoded:
                                os.remove(p)
                                mitigated += 1
                                audit.log_event("BLUE", "FIREWALL_BLOCK", {"file": p, "threat": "C2_BEACON"})
                        except Exception:
                            pass # Not base64 or not interesting
                    except Exception:
                        pass

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

            # --- SOAR PLAYBOOKS (DEFCON Logic) ---
            # Blue logic maps alert 1-5 (Low-High). Config Defcon maps 5-1 (Low-High) inversely usually,
            # but let's assume config.MAX_ALERT (5) is severe.
            # config.DEFCON_LEVELS: {5: "NORMAL"...} implies 5 is good.
            # Let's map Alert Level (1-5, 5 is bad) to SOAR actions.

            if current_alert >= 3:
                # Playbook: FLUSH_DNS (Clean Network Bus)
                packets = glob.glob(os.path.join(config.NETWORK_BUS_DIR, '*'))
                if packets:
                    logger.warning("SOAR: High Alert - Flushing Network Bus.")
                    for p in packets:
                        try: os.remove(p)
                        except Exception: pass

            if current_alert == 5:
                # Playbook: ISOLATE_HOST (Quarantine simulation data)
                # In a real sim we'd move dirs, but that breaks Red loop.
                # Instead, we'll nuke all non-honeypot files.
                logger.critical("SOAR: DEFCON 1 - NUCLEAR OPTION - Purging all non-critical data.")
                all_files = glob.glob(os.path.join(config.SIMULATION_DATA_DIR, '*'))
                for f in all_files:
                    if os.path.basename(f) not in config.HONEYPOT_NAMES:
                        try: os.remove(f)
                        except Exception: pass
            
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
