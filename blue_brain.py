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
import secrets
import math
import signal
import sys
import hashlib
import subprocess

import utils
import config
from typing import List, Tuple, Dict, Any

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

class BlueDefender:
    """
    Blue Team AI Agent implementing NIST SP 800-61 Incident Response policy.
    Uses Q-Learning to adapt defensive strategies.
    """
    def __init__(self) -> None:
        self.running: bool = True
        self.epsilon: float = config.AI_PARAMS['EPSILON_START']
        self.alpha: float = config.AI_PARAMS['ALPHA']
        self.q_table: Dict[str, float] = {}
        self.audit_logger = utils.AuditLogger(config.AUDIT_LOG)
        self.tracer = utils.TraceLogger(config.TRACE_LOG)
        self.backup_created: bool = False
        self.fim_baseline: Dict[str, str] = {}

        # Signal Handling
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

        self.setup()

    def setup(self) -> None:
        """Initialize resources and load persistent state."""
        print(f"{C_CYAN}[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61{C_RESET}")
        self.q_table = utils.access_memory(config.Q_TABLE_BLUE) or {}
        if not os.path.exists(config.INCIDENT_DIR):
            os.makedirs(config.INCIDENT_DIR)

        # Establish FIM Baseline
        if os.path.exists(config.CRITICAL_DIR):
            for f in os.listdir(config.CRITICAL_DIR):
                path = os.path.join(config.CRITICAL_DIR, f)
                try:
                    with open(path, 'rb') as file:
                        self.fim_baseline[path] = hashlib.sha256(file.read()).hexdigest()
                except OSError: pass

    def shutdown(self, signum: int, frame: Any) -> None:
        """Graceful shutdown handler."""
        print(f"\n{C_CYAN}[SYSTEM] Blue Team shutting down gracefully...{C_RESET}")
        utils.access_memory(config.Q_TABLE_BLUE, self.q_table)
        self.running = False
        sys.exit(0)

    def scan_network(self) -> List[str]:
        """Check for suspicious listening ports > 1024 (Simulating socket scanning)."""
        suspicious_ports = []
        try:
            # Use 'ss' to list listening tcp ports
            output = subprocess.check_output(["ss", "-tlnH"], text=True)
            for line in output.splitlines():
                parts = line.split()
                if len(parts) > 3:
                    address = parts[3] # e.g. 127.0.0.1:8080
                    if ':' in address:
                        port_str = address.split(':')[-1]
                        if port_str.isdigit():
                            port = int(port_str)
                            if port > 8000 and port < 9000: # We know Red range
                                suspicious_ports.append(str(port))
        except (OSError, subprocess.CalledProcessError): pass
        return suspicious_ports

    def scan_processes(self) -> List[int]:
        """Scan for malicious processes (malware.py) using pgrip pattern."""
        pids = []
        try:
            # Use pgrep for more reliable PID detection
            # -f matches against full command line
            output = subprocess.check_output(["pgrep", "-f", "payloads/malware.py"], text=True)
            for pid_str in output.splitlines():
                if pid_str.isdigit():
                    pids.append(int(pid_str))
        except (OSError, subprocess.CalledProcessError): pass
        return pids

    def get_state(self, current_alert: int) -> Tuple[str, List[str], List[str], List[str], List[str], List[str]]:
        """
        Scan environment and determine current state.
        Now includes Network and Process intelligence.
        """
        visible_threats = glob.glob(os.path.join(config.WAR_ZONE_DIR, 'malware_*'))
        hidden_threats = glob.glob(os.path.join(config.WAR_ZONE_DIR, '.sys_*'))
        c2_beacons = glob.glob(os.path.join(config.WAR_ZONE_DIR, '*.c2_beacon'))
        encrypted_files = glob.glob(os.path.join(config.WAR_ZONE_DIR, '*.enc'))

        # USB / Removable Media
        usb_dir = os.path.join(config.WAR_ZONE_DIR, "usb")
        usb_files = []
        if os.path.exists(usb_dir):
            usb_files = [os.path.join(usb_dir, f) for f in os.listdir(usb_dir)]

        # Add active processes/ports to threat count
        active_pids = self.scan_processes()
        active_ports = self.scan_network()

        all_threats = visible_threats + hidden_threats + c2_beacons + encrypted_files + usb_files
        threat_count = len(all_threats) + len(active_pids) + len(active_ports)

        # State key complexity increases
        return f"{current_alert}_{threat_count}", visible_threats, hidden_threats, c2_beacons, encrypted_files, all_threats

    def choose_action(self, state_key: str) -> str:
        """Select an action using Epsilon-Greedy strategy."""
        if (secrets.randbelow(100) / 100.0) < self.epsilon:
            return secrets.choice(config.BLUE_ACTIONS)
        else:
            known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in config.BLUE_ACTIONS}
            return max(known, key=known.get)

    def report_incident(self, filepath: str, threat_type: str, action_taken: str) -> None:
        """Generate a forensic incident report."""
        try:
            timestamp = time.time()
            file_hash = "unknown"
            if os.path.exists(filepath):
                 with open(filepath, 'rb') as f:
                     file_hash = hashlib.sha256(f.read()).hexdigest()
            
            report = {
                'id': hashlib.md5(f"{timestamp}{filepath}".encode()).hexdigest(),
                'timestamp': timestamp,
                'threat_type': threat_type,
                'filepath': filepath,
                'file_hash': file_hash,
                'action': action_taken,
                'status': 'MITIGATED'
            }
            
            report_path = os.path.join(config.INCIDENT_DIR, f"report_{report['id']}.json")
            utils.secure_create(report_path, json.dumps(report, indent=4))
            self.audit_logger.log_event("BLUE", "INCIDENT_REPORT", f"Report {report['id']} generated for {filepath}")
        except (OSError, TypeError) as e:
            # print(f"Reporting Error: {e}")
            pass

    def run(self) -> None:
        iteration = 0
        while self.running:
            try:
                with self.tracer.context("BLUE_MAIN_LOOP"):
                    iteration += 1

                    # 1. OBSERVE
                    war_state = utils.access_memory(config.STATE_FILE) or {'blue_alert_level': 1}
                current_alert = war_state.get('blue_alert_level', 1)

                state_key, visible, hidden, c2, encrypted, all_threats = self.get_state(current_alert)
                threat_count = len(all_threats)

                # 2. DECIDE
                action = self.choose_action(state_key)

                # Decay Epsilon/Alpha
                self.epsilon = max(config.AI_PARAMS['MIN_EPSILON'], self.epsilon * config.AI_PARAMS['EPSILON_DECAY'])
                self.alpha = max(0.1, self.alpha * config.AI_PARAMS['ALPHA_DECAY'])

                # 3. ACT
                mitigated = 0
                restored = 0

                if action == "SIGNATURE_SCAN":
                    # Check known signatures
                    known_sigs = utils.access_memory(config.SIGNATURE_FILE) or {}

                    for t in all_threats:
                        try:
                            sz = os.path.getsize(t)
                            if str(sz) in known_sigs:
                                self.report_incident(t, "KNOWN_SIGNATURE", "DELETE")
                                os.remove(t)
                                mitigated += 1
                        except OSError: pass

                    # Visible cleanup
                    for t in visible:
                        if os.path.exists(t):
                            try:
                                self.report_incident(t, "VISIBLE_THREAT", "DELETE")
                                os.remove(t); mitigated += 1
                            except OSError: pass

                elif action == "HEURISTIC_SCAN":
                    # 1. Kill Processes
                    active_pids = self.scan_processes()
                    for pid in active_pids:
                        try:
                            os.kill(pid, signal.SIGKILL)
                            mitigated += 1
                            print(f"{C_BLUE}[DEFENSE] Killed Active Malware PID: {pid}{C_RESET}")
                            self.audit_logger.log_event("BLUE", "PROCESS_KILL", f"Killed PID {pid}")
                        except OSError: pass

                    # 2. FIM Check
                    for path, baseline_hash in self.fim_baseline.items():
                        if os.path.exists(path):
                            try:
                                with open(path, 'rb') as f:
                                    current_hash = hashlib.sha256(f.read()).hexdigest()
                                if current_hash != baseline_hash:
                                    self.report_incident(path, "INTEGRITY_VIOLATION", "RESTORE")
                                    print(f"{C_BLUE}[DEFENSE] FIM Alert: {path} modified!{C_RESET}")
                                    mitigated += 1
                            except OSError: pass

                    # 3. File Scan
                    for t in all_threats:
                        if not os.path.exists(t): continue

                        # Correct: Read file content for entropy calculation
                        content_head = utils.read_file_head(t, 4096)
                        entropy = utils.calculate_entropy(content_head)
                        is_c2 = t.endswith(".c2_beacon")

                        if ".sys" in t or entropy > 3.5 or is_c2:
                            try:
                                # Learn Signature
                                sz = os.path.getsize(t)
                                sigs = utils.access_memory(config.SIGNATURE_FILE) or {}
                                if str(sz) not in sigs:
                                    sigs[str(sz)] = entropy
                                    utils.access_memory(config.SIGNATURE_FILE, sigs)
                                    print(f"{C_BLUE}[BLUE LEARNING] Learned signature: Size {sz} | Entropy {entropy:.2f}{C_RESET}")

                                threat_type = "C2_BEACON" if is_c2 else ("HIDDEN_ROOTKIT" if ".sys" in t else "HIGH_ENTROPY")
                                self.report_incident(t, threat_type, "DELETE")

                                os.remove(t)
                                mitigated += 1
                            except OSError: pass

                elif action == "DEPLOY_DECOY":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"accounts_{1000 + secrets.randbelow(9000)}.honey")
                    try:
                        utils.secure_create(fname, "admin:password123")
                        print(f"{C_BLUE}[DEFENSE] Deployed Honey Token: {fname}{C_RESET}")
                    except OSError: pass

                elif action == "DEPLOY_TRAP":
                    fname = os.path.join(config.WAR_ZONE_DIR, f"backup_{100 + secrets.randbelow(900)}.tar_pit")
                    try:
                        # Large empty file
                        with open(fname, 'wb') as f: f.truncate(1024 * 1024 * 50) # 50MB sparse file
                    except OSError: pass

                elif action == "BACKUP_CRITICAL":
                    self.backup_created = True
                    # In a real sim we'd copy files. Here we just set a flag and maybe creating a marker
                    pass

                elif action == "RESTORE_CRITICAL":
                    if self.backup_created and encrypted:
                        for enc in encrypted:
                            try:
                                # Restore logic: Rename .enc back to original (simulated restore)
                                orig = enc.replace(".enc", "")
                                os.rename(enc, orig)
                                restored += 1
                                self.report_incident(enc, "RANSOMWARE_RECOVERY", "RESTORE")
                            except OSError: pass

                # 4. REWARD

                # 4. REWARD
                reward = 0
                if mitigated > 0: reward = config.BLUE_REWARDS['MITIGATION']
                if restored > 0: reward = config.BLUE_REWARDS['RESTORE_SUCCESS']
                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = config.BLUE_REWARDS['WASTE']
                if current_alert >= 4 and action == "OBSERVE": reward = config.BLUE_REWARDS['PATIENCE']
                if action == "IGNORE" and threat_count > 0: reward = config.BLUE_REWARDS['NEGLIGENCE']

                # Check for Honeypot Triggers (Simulated via external feedback or Red logs?
                # Ideally Red reports getting trapped, or Blue checks if honeypot was modified.
                # For this sim, we rely on Audit Log? Or state?
                # Simplification: We can't easily see if Red touched it unless Red changed it.
                # Assuming Red's 'TRAPPED' reward handles their penalty. Blue needs a signal.
                # We'll skip Blue's explicit reward for now unless we implement file access monitoring.)

                # 5. LEARN (Q-Learning)
                old_val = self.q_table.get(f"{state_key}_{action}", 0)
                next_max = max([self.q_table.get(f"{state_key}_{a}", 0) for a in config.BLUE_ACTIONS])
                new_val = old_val + self.alpha * (reward + config.AI_PARAMS['GAMMA'] * next_max - old_val)
                self.q_table[f"{state_key}_{action}"] = new_val

                if iteration % config.AI_PARAMS['SYNC_INTERVAL'] == 0:
                    utils.access_memory(config.Q_TABLE_BLUE, self.q_table)

                # 6. UPDATE STATE
                if mitigated > 0 and current_alert < config.MAX_ALERT:
                    war_state['blue_alert_level'] = min(config.MAX_ALERT, current_alert + 1)
                elif mitigated == 0 and current_alert > config.MIN_ALERT and action == "OBSERVE":
                    war_state['blue_alert_level'] = max(config.MIN_ALERT, current_alert - 1)

                # Deep Clean Protocol at MAX ALERT
                if current_alert == config.MAX_ALERT and threat_count > 10:
                    print(f"{C_BLUE}[DEFENSE] ALERT MAX: Initiating Deep Clean Protocol...{C_RESET}")
                    try:
                        cleaner_path = os.path.join(config.BASE_DIR, "tools", "clean.py")
                        subprocess.run([sys.executable, cleaner_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except: pass

                utils.access_memory(config.STATE_FILE, war_state)

                # LOG
                icon = "🛡️" if mitigated == 0 else "⚔️"
                print(f"{C_BLUE}[BLUE AI]{C_RESET} {icon} State: {state_key} | Action: {action} | Kill: {mitigated} | Q: {new_val:.2f}")

                time.sleep(0.5 if current_alert >= 4 else 1.0)

            except Exception as e:
                # print(f"Blue Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    bot = BlueDefender()
    bot.run()
