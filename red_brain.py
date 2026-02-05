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
import config
import payload_factory
import urllib.request
import urllib.error

# --- SYSTEM CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
THREAT_DB_FILE = os.path.join(BASE_DIR, "threat_db.json")
TARGET_DIR = config.TARGET_DIR

# --- LOGGING ---
logger = utils.setup_logging("RED", os.path.join(config.LOG_DIR, "red.log"))

# --- AI HYPERPARAMETERS ---
ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK", "T1036_MASQUERADE", "T1486_ENCRYPT", "T1070_CLEANUP", "T1190_WEB_EXPLOIT", "T1003_CREDENTIAL_DUMPING"]

# User-Agent Spoofing
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "sqlmap/1.5.2#stable", # Obvious for noise
]

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
    logger.info(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")

    # Load Q-Table (SQLite)
    q_manager = utils.QTableManager("red", ACTIONS)

    threat_loader = utils.SmartJSONLoader(THREAT_DB_FILE, {'hashes': [], 'filenames': []})
    payload_gen = payload_factory.PayloadGenerator()
    step_count = 0

    # Feedback Loop State
    last_web_attack_id = None

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
            
            # Optimization: Using Structural Pattern Matching (Python 3.10+)
            match action:
                case "T1046_RECON":
                    # Low Entropy Bait
                    fname = f"{TARGET_DIR}/malware_bait_{timestamp}.sh"
                    try:
                        with open(fname, 'w') as f: f.write("echo 'scan'")
                        impact = 1
                    except: pass

                case "T1027_OBFUSCATE":
                    # High Entropy Binary with Polymorphism
                    # 1. Base Name
                    fname = f"{TARGET_DIR}/malware_crypt_{timestamp}.bin"

                    # 2. Polymorphic Content (Random padding to change Hash)
                    # In real life, we'd mutate code. Here, we append junk.
                    padding_size = random.randint(1, 256)
                    payload = b"MALICIOUS_PAYLOAD" + os.urandom(1024) + os.urandom(padding_size)

                    try:
                        with open(fname, 'wb') as f: f.write(payload)
                        impact = 3
                    except: pass

                case "T1003_ROOTKIT":
                    # Hidden File
                    fname = f"{TARGET_DIR}/.sys_shadow_{timestamp}"
                    try:
                        with open(fname, 'w') as f: f.write("uid=0(root)")
                        impact = 5
                    except: pass

                case "T1036_MASQUERADE":
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

                case "T1589_LURK":
                    impact = 0

                case "T1486_ENCRYPT":
                    # REAL Ransomware: XOR Encryption
                    try:
                        files = [f.path for f in os.scandir(TARGET_DIR) if f.is_file() and not f.name.endswith('.enc')]
                        if files:
                            target = _choice(files)

                            # Read - Encrypt - Write
                            key = 0xAA # Simple XOR key
                            with open(target, 'rb') as f: data = bytearray(f.read())
                            for i in range(len(data)): data[i] ^= key

                            new_name = target + ".enc"
                            with open(new_name, 'wb') as f: f.write(data)

                            utils.secure_delete(target) # Delete original

                            logger.info(f"RANSOMWARE: Encrypted {os.path.basename(target)}")
                            impact = 8
                    except: pass

                case "T1070_CLEANUP":
                    # Anti-forensics: Delete logs or self
                    try:
                        # Delete self-dropped scripts
                        files = [f.path for f in os.scandir(TARGET_DIR) if f.name.startswith('malware_')]
                        if files:
                            target = _choice(files)
                            utils.secure_delete(target)
                            impact = 2 # Low impact but good for evasion
                    except: pass

                case "T1190_WEB_EXPLOIT":
                    # LIVE FIRE: Real HTTP Attack against localhost:5000
                    atype = _choice(["SQLi", "XSS", "RCE"])
                    payload = payload_gen.generate(atype)

                    # Encode payload
                    encoded = urllib.parse.quote(payload)
                    url = f"http://127.0.0.1:5000/?q={encoded}"

                    # Rotate User-Agents to evade simple blocks
                    ua = _choice(USER_AGENTS)

                    try:
                        req = urllib.request.Request(url, headers={'User-Agent': ua})
                        with urllib.request.urlopen(req, timeout=1) as response:
                            if response.status == 200:
                                reward += 10
                                logger.info(f"ATTACK SUCCESS: Payload '{payload[:20]}...' executed (200 OK)")
                                impact = 8
                    except urllib.error.HTTPError as e:
                        if e.code == 403:
                            reward -= 10 # Higher penalty for getting burned
                            logger.warning("ATTACK BLOCKED: Target Adapted. Initiating 'Low and Slow' Evasion.")
                            # Low and Slow: Sleep longer to let bucket/alert level decay
                            time.sleep(5)
                    except Exception as e:
                        pass

                case "T1003_CREDENTIAL_DUMPING":
                    # Simulated Credential Access
                    try:
                        # Look for leaked DBs from successful SQLi
                        dumps = [f.path for f in os.scandir(TARGET_DIR) if "leaked" in f.name]
                        if dumps:
                            logger.info("CREDENTIALS ACQUIRED from Previous Breach!")
                            reward += 15
                            # Steal and delete (simulated exfil)
                            utils.secure_delete(dumps[0])
                            impact = 9
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
            
            logger.info(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")
            
            # Adaptive sleep based on impact
            activity = 1.0 if impact > 0 else 0.0
            utils.adaptive_sleep(1.0, activity)
            
        except KeyboardInterrupt:
            break
        except Exception:
            _sleep(1)

if __name__ == "__main__":
    engage_offense()
