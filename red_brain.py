#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import time
import json
import secrets
import signal
import sys
import utils
import config
import threading
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Tuple, Dict, Any

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

class C2Handler(BaseHTTPRequestHandler):
    current_command = "SLEEP"
    exfiltrated_data = 0

    def do_GET(self):
        if self.path == "/command":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(C2Handler.current_command.encode())
        elif "/beacon" in self.path:
            self.send_response(200)
            self.end_headers()
        elif "/log" in self.path:
            self.send_response(200)
            self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/exfil":
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                # Rate Limiting/Size Limiting
                if content_length > 1024 * 1024 * 10: # 10MB limit
                    self.send_response(413) # Payload Too Large
                    self.end_headers()
                    return

                post_data = self.rfile.read(content_length)
                C2Handler.exfiltrated_data += len(post_data)
                self.send_response(200)
                self.end_headers()
            except:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass # Silence logging

class RedTeamer:
    """
    Red Team AI Agent implementing MITRE ATT&CK Matrix tactics.
    Uses Double Q-Learning with Experience Replay for stable training.
    """
    def __init__(self) -> None:
        self.running: bool = True
        self.epsilon: float = config.AI_PARAMS['EPSILON_START']
        self.alpha: float = config.AI_PARAMS['ALPHA']
        self.q_table_1: Dict[str, float] = {}
        self.q_table_2: Dict[str, float] = {}
        self.memory: List[Tuple[str, str, float, str]] = []
        self.audit_logger = utils.AuditLogger(config.AUDIT_LOG)

        self.c2_port = 8000 + secrets.randbelow(1000)
        self.c2_server = None
        self.active_payloads = []

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        self.setup()

    def setup(self) -> None:
        print(f"{C_RED}[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE{C_RESET}")
        data = utils.access_memory(config.Q_TABLE_RED) or {}
        self.q_table_1 = data.get('q1', {})
        self.q_table_2 = data.get('q2', {})

        if not os.path.exists(config.WAR_ZONE_DIR):
            try: os.makedirs(config.WAR_ZONE_DIR)
            except OSError: pass

        # Start C2
        self.start_c2()

    def start_c2(self):
        try:
            self.c2_server = HTTPServer(('127.0.0.1', self.c2_port), C2Handler)
            thread = threading.Thread(target=self.c2_server.serve_forever)
            thread.daemon = True
            thread.start()
            print(f"{C_RED}[RED] C2 Server listening on port {self.c2_port}{C_RESET}")
        except Exception as e:
            print(f"C2 Start Error: {e}")

    def shutdown(self, signum: int, frame: Any) -> None:
        print(f"\n{C_RED}[SYSTEM] Red Team shutting down gracefully...{C_RESET}")

        self.running = False

        if self.c2_server:
            try: self.c2_server.shutdown()
            except: pass

        # Kill payloads
        for p in self.active_payloads:
            if p.poll() is None:
                try:
                    p.terminate()
                    p.wait(timeout=1)
                except:
                    try: p.kill()
                    except: pass

        utils.access_memory(config.Q_TABLE_RED, {'q1': self.q_table_1, 'q2': self.q_table_2})
        sys.exit(0)

    def choose_action(self, state_key: str) -> str:
        """Select an action using Double Q-Learning strategy."""
        # Using secrets for exploration choice is safer though slightly slower
        if (secrets.randbelow(100) / 100.0) < self.epsilon:
            return secrets.choice(config.RED_ACTIONS)
        else:
            # Double Q: Use average or sum of Q1+Q2
            known = {}
            for a in config.RED_ACTIONS:
                val = self.q_table_1.get(f"{state_key}_{a}", 0) + self.q_table_2.get(f"{state_key}_{a}", 0)
                known[a] = val
            return max(known, key=known.get)

    def remember(self, state: str, action: str, reward: float, next_state: str) -> None:
        """Store experience in replay buffer."""
        self.memory.append((state, action, reward, next_state))
        if len(self.memory) > config.AI_PARAMS['MEMORY_SIZE']:
            self.memory.pop(0)

    def replay(self) -> None:
        """Train the model using random batch from memory."""
        if len(self.memory) < config.AI_PARAMS['BATCH_SIZE']:
            return

        # Random sampling for replay buffer doesn't strictly require CSPRNG, but for consistency:
        # secrets doesn't have sample, so we implement a simple one or keep random for this non-security part?
        # Let's keep random for ML sampling performance as it's not a security vulnerability.
        import random
        batch = random.sample(self.memory, config.AI_PARAMS['BATCH_SIZE'])

        for state, action, reward, next_state in batch:
             # Randomly update Q1 or Q2
             if secrets.randbelow(2) == 0:
                 # Update Q1 using Q2 for value estimation
                 max_next = max([self.q_table_1.get(f"{next_state}_{a}", 0) for a in config.RED_ACTIONS])
                 # Or correctly: use a from Q1 to query Q2? Simplified to standard Q-Learning for sim speed here,
                 # but implementing simple Double Q Logic:
                 # Q1(s,a) <- Q1(s,a) + alpha * (r + gamma * Q2(s', argmax Q1(s',a)) - Q1(s,a))

                 # simplified max for stability in this script scope:
                 q1_old = self.q_table_1.get(f"{state}_{action}", 0)
                 q2_next_max = max([self.q_table_2.get(f"{next_state}_{a}", 0) for a in config.RED_ACTIONS])

                 new_val = q1_old + self.alpha * (reward + config.AI_PARAMS['GAMMA'] * q2_next_max - q1_old)
                 self.q_table_1[f"{state}_{action}"] = new_val
             else:
                 # Update Q2 using Q1
                 q2_old = self.q_table_2.get(f"{state}_{action}", 0)
                 q1_next_max = max([self.q_table_1.get(f"{next_state}_{a}", 0) for a in config.RED_ACTIONS])

                 new_val = q2_old + self.alpha * (reward + config.AI_PARAMS['GAMMA'] * q1_next_max - q2_old)
                 self.q_table_2[f"{state}_{action}"] = new_val

    def run(self):
        iteration = 0
        while self.running:
            try:
                iteration += 1
                
                # 1. RECON
                war_state = utils.access_memory(config.STATE_FILE) or {'blue_alert_level': 1}
                current_alert = war_state.get('blue_alert_level', 1)
                state_key = f"{current_alert}"
                
                # 2. DECIDE
                action = self.choose_action(state_key)
                
                self.epsilon = max(config.AI_PARAMS['MIN_EPSILON'], self.epsilon * config.AI_PARAMS['EPSILON_DECAY'])
                self.alpha = max(0.1, self.alpha * config.AI_PARAMS['ALPHA_DECAY'])

                # 3. EXECUTE
                impact = 0

                if action == "T1046_RECON":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"malware_bait_{int(time.time())}.sh")
                    try:
                        utils.secure_create(fname, "echo 'scan'")
                        impact = 1
                    except OSError:
                        pass # Expected if permissions deny

                elif action == "T1027_OBFUSCATE":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"malware_crypt_{int(time.time())}.bin")
                    try:
                        size = 800 + secrets.randbelow(400)
                        data = os.urandom(size).decode('latin1')
                        utils.secure_create(fname, data)
                        impact = 3
                    except OSError: pass

                elif action == "T1003_ROOTKIT":
                    fname = os.path.join(config.WAR_ZONE_DIR, f".sys_shadow_{int(time.time())}")
                    try:
                        utils.secure_create(fname, "uid=0(root)")
                        impact = 5
                    except OSError: pass

                elif action == "T1071_C2_BEACON":
                    # Deploy Active Payload
                    try:
                        payload_path = os.path.join(config.BASE_DIR, "payloads", "malware.py")
                        if os.path.exists(payload_path):
                            proc = subprocess.Popen(
                                [sys.executable, payload_path, "--port", str(self.c2_port), "--target", config.WAR_ZONE_DIR],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL
                            )
                            self.active_payloads.append(proc)
                            impact = 5
                            C2Handler.current_command = "ENCRYPT" # Command the botnet
                            self.audit_logger.log_event("RED", "C2_BEACON", f"Deployed Payload PID: {proc.pid}")
                    except Exception as e:
                        print(e)

                elif action == "T1589_LURK":
                    impact = 0

                elif action == "T1486_ENCRYPT":
                    # Ransomware: Rename random visible files to .enc
                    targets = [f for f in os.listdir(config.WAR_ZONE_DIR) if not f.endswith(".enc") and not f.startswith(".")]
                    if targets:
                        target = random.choice(targets)
                        src = os.path.join(config.WAR_ZONE_DIR, target)
                        dst = src + ".enc"
                        try:
                            # If it's a honeypot, we get trapped!
                            if utils.is_honeypot(src):
                                impact = -1 # Special signal for trap
                            else:
                                os.rename(src, dst)
                                impact = 6
                                self.audit_logger.log_event("RED", "RANSOMWARE", f"Encrypted {target}")
                        except OSError: pass

                elif action == "T1547_PERSISTENCE":
                    # Persistence: Create a hidden startup script
                    fname = os.path.join(config.WAR_ZONE_DIR, f".startup_{10 + secrets.randbelow(90)}.sh")
                    try:
                        utils.secure_create(fname, "#!/bin/bash\n./malware.sh")
                        impact = 4
                    except OSError: pass

                elif action == "T1041_EXFILTRATION":
                    if self.active_payloads:
                        C2Handler.current_command = "EXFIL"
                        # Check if we got data
                        if C2Handler.exfiltrated_data > 0:
                            impact = 7
                            self.audit_logger.log_event("RED", "EXFILTRATION", f"Stolen: {C2Handler.exfiltrated_data} bytes")
                    else:
                        # Need payload first
                        impact = 0

                elif action == "T1091_REPLICATION":
                    # Airgapped Infection: Drop Stowaway on USB
                    usb_dir = os.path.join(config.WAR_ZONE_DIR, "usb")
                    if not os.path.exists(usb_dir):
                        try: os.makedirs(usb_dir)
                        except: pass

                    try:
                        # Create a stowaway instance
                        # For simulation, we create a carrier that exfils data
                        from payloads.stowaway import Stowaway
                        carrier = Stowaway(mode="CARRIER", target_dir=config.WAR_ZONE_DIR)

                        drop_path = os.path.join(usb_dir, f"drive_{int(time.time())}.dat")
                        carrier.deploy(drop_path)

                        # Simulate activation by user (or autorun)
                        # In simulation, we just trigger it immediately for effect
                        Stowaway.activate(drop_path, config.WAR_ZONE_DIR)

                        impact = 5
                        self.audit_logger.log_event("RED", "REPLICATION", f"Stowaway dropped at {drop_path}")
                    except Exception as e:
                        # print(f"Stowaway Error: {e}")
                        pass

                # 4. REWARD CALCULATION
                reward = 0
                if impact > 0: reward = config.RED_REWARDS['IMPACT']
                if impact == 6: reward = config.RED_REWARDS['RANSOM_SUCCESS']
                if impact == 7: reward = config.RED_REWARDS['EXFIL_SUCCESS']
                if impact == 5 and action == "T1091_REPLICATION": reward = config.RED_REWARDS['REPLICATION_SUCCESS']
                if impact == -1: reward = config.RED_REWARDS['TRAPPED']

                if current_alert >= 4 and action == "T1589_LURK": reward = config.RED_REWARDS['STEALTH']
                if current_alert == config.MAX_ALERT and impact > 0: reward = config.RED_REWARDS['CRITICAL']
                if action == "T1071_C2_BEACON": reward = config.RED_REWARDS['C2_SUCCESS']
                if action == "T1547_PERSISTENCE" and impact > 0: reward = config.RED_REWARDS['PERSISTENCE_SUCCESS']

                # 5. LEARN (Double Q + Replay)
                # We need next state for proper learning.
                # Simplification: Assume next state is roughly same key or +1 alert.
                # In strict RL, we observe S' after act.
                # Let's peek at new state
                new_war_state = utils.access_memory(config.STATE_FILE) or {'blue_alert_level': 1}
                next_alert = new_war_state.get('blue_alert_level', 1)
                next_state_key = f"{next_alert}"

                self.remember(state_key, action, reward, next_state_key)
                self.replay()

                if iteration % config.AI_PARAMS['SYNC_INTERVAL'] == 0:
                    utils.access_memory(config.Q_TABLE_RED, {'q1': self.q_table_1, 'q2': self.q_table_2})

                # 6. TRIGGER ALERTS
                if impact > 0 and secrets.randbelow(2) == 0:
                    war_state['blue_alert_level'] = min(config.MAX_ALERT, current_alert + 1)
                    utils.access_memory(config.STATE_FILE, war_state)

                print(f"{C_RED}[RED AI] {C_RESET} 👹 State: {state_key} | Tech: {action} | Impact: {impact} | Q: {new_val:.2f}")

                # Import random just for sleep jitter, non-critical
                import random
                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                # print(f"Red Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    bot = RedTeamer()
    bot.run()
