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
import signal
import sys
import logging
import hashlib
import collections
from typing import Dict, Any, List, Deque, Set

import utils
import config
import ml_engine
from agent_base import CyberAgent

# Setup Logging (Kept for SignatureDatabase usage if needed, though agent_base handles main log)
logger = logging.getLogger("BlueTeam")

class SignatureDatabase:
    """Manages known bad file hashes (Adaptive Immunity)."""
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.signatures: Set[str] = set()
        self.load()

    def load(self):
        data = utils.safe_json_read(self.filepath)
        if isinstance(data, list):
            self.signatures = set(data)

    def save(self):
        utils.safe_json_write(self.filepath, list(self.signatures))

    def add_signature(self, file_content: bytes):
        file_hash = hashlib.sha256(file_content).hexdigest()
        if file_hash not in self.signatures:
            self.signatures.add(file_hash)
            self.save()
            logger.info(f"Learned new signature: {file_hash[:8]}...")

    def check_signature(self, file_content: bytes) -> bool:
        file_hash = hashlib.sha256(file_content).hexdigest()
        return file_hash in self.signatures

class BlueDefender(CyberAgent):
    def __init__(self):
        super().__init__("BLUE", config.BLUE["ACTIONS"], config.PATHS["LOG_BLUE"])
        self.signature_db = SignatureDatabase(config.PATHS["SIGNATURES"])
        self.backups: Dict[str, bytes] = {}

    def perceive(self) -> str:
        war_state = self.state_manager.get_war_state()
        current_alert = war_state.get('blue_alert_level', 1)

        # Simple volume estimation
        try:
            threat_volume = len(os.listdir(config.PATHS["WAR_ZONE"]))
        except: threat_volume = 0

        return f"{current_alert}_{1 if threat_volume > 5 else 0}_{1 if self.backups else 0}"

    def get_context(self) -> Dict[str, Any]:
        try:
            threat_volume = len(os.listdir(config.PATHS["WAR_ZONE"]))
        except: threat_volume = 0

        return {
            "alert_level": self.state_manager.get_war_state().get('blue_alert_level', 1),
            "threat_count": threat_volume,
            "has_backup": len(self.backups) > 0
        }

    def calculate_reward(self, action_name: str, result: Dict[str, Any]) -> float:
        mitigated = result.get("mitigated", 0) + result.get("killed", 0)
        restored = result.get("restored", 0)
        reward = 0.0

        if mitigated > 0: reward += config.BLUE["REWARDS"]["MITIGATION"]
        if restored > 0: reward += config.BLUE["REWARDS"]["RESTORE_SUCCESS"]
        if action_name == "BACKUP_CRITICAL" and result.get("backed_up", 0) > 0: reward += 5

        # Alert Update Side Effect
        current_alert = self.state_manager.get_war_state().get('blue_alert_level', 1)
        if mitigated > 0 and current_alert < config.SYSTEM["MAX_ALERT_LEVEL"]:
             self.state_manager.update_war_state({'blue_alert_level': min(config.SYSTEM["MAX_ALERT_LEVEL"], current_alert + 1)})

        return reward

    # --- TACTICS ---
    def signature_scan(self):
        mitigated = 0
        if not os.path.exists(config.PATHS["WAR_ZONE"]): return {"mitigated": 0}
        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file():
                        if "c2_beacon" in entry.name or utils.scan_threats(entry.path):
                            os.remove(entry.path)
                            mitigated += 1
        except: pass
        return {"mitigated": mitigated}

    def heuristic_scan(self):
        mitigated = 0
        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file() and not utils.is_tar_pit(entry.path) and not utils.is_honeypot(entry.path):
                        try:
                            if entry.name.endswith(".enc"): continue
                            # Use binary read for entropy calculation to handle non-text files correctly
                            entropy = utils.calculate_entropy(utils.safe_file_read(entry.path, 0.1, binary=True))
                            if entropy > 3.5:
                                os.remove(entry.path)
                                mitigated += 1
                        except: pass
        except: pass
        return {"mitigated": mitigated}

    def backup_critical(self):
        count = 0
        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file() and not entry.name.endswith(".enc"):
                        if not utils.is_tar_pit(entry.path) and not "malware" in entry.name:
                            try:
                                # Backup as binary to preserve integrity
                                self.backups[entry.name] = utils.safe_file_read(entry.path, binary=True)
                                count += 1
                            except: pass
        except: pass
        return {"backed_up": count}

    def restore_data(self):
        restored = 0
        try:
            with os.scandir(config.PATHS["WAR_ZONE"]) as it:
                for entry in it:
                    if entry.is_file() and entry.name.endswith(".enc"):
                        original_name = entry.name[:-4]
                        if original_name in self.backups:
                            os.remove(entry.path)
                            # Restore as binary
                            with open(os.path.join(config.PATHS["WAR_ZONE"], original_name), 'wb') as f:
                                f.write(self.backups[original_name])
                            restored += 1
        except: pass
        return {"restored": restored}

    def deploy_trap(self):
        if not os.path.exists(config.PATHS["WAR_ZONE"]): return {}
        utils.create_tar_pit(os.path.join(config.PATHS["WAR_ZONE"], "access.log"))
        utils.create_logic_bomb(os.path.join(config.PATHS["WAR_ZONE"], "shadow_backup"))
        return {"status": "deployed"}

    def deploy_decoy(self):
        return self.deploy_trap()

    def observe(self):
        return {"status": "observing"}

    def ignore(self):
        return {"status": "ignoring"}

    def hunt_processes(self):
        killed = 0
        if os.path.exists(config.PATHS["PROC"]):
             try:
                with os.scandir(config.PATHS["PROC"]) as it:
                    for entry in it:
                        # Emulation: Read the Real PID from the meta-file and kill it
                        try:
                            content = utils.safe_file_read(entry.path)
                            if "real_pid" in content:
                                for line in content.splitlines():
                                    if line.startswith("real_pid:"):
                                        pid = int(line.split(":")[1].strip())
                                        # Kill the actual process
                                        try:
                                            os.kill(pid, signal.SIGTERM)
                                            logger.info(f"Killed Real Ghost Process: {pid}")
                                        except ProcessLookupError: pass # Already dead
                                        except PermissionError: pass
                        except: pass

                        # Remove the marker file
                        os.remove(entry.path)
                        killed += 1
             except: pass
        return {"killed": killed}

    def verify_integrity(self):
        return {"status": "verifying"}

    def deception_engine(self):
        # Advanced: Deploy HoneyTokens (fake credentials)
        count = 0
        if not os.path.exists(config.PATHS["WAR_ZONE"]): return {}
        try:
            # Create a fake user/pass file that looks tasty
            trap_file = os.path.join(config.PATHS["WAR_ZONE"], "aws_keys.json")
            utils.create_tar_pit(trap_file) # Actually a trap
            count += 1
        except: pass
        return {"deployed": count, "type": "HoneyToken"}

    def isolate_zone(self):
        return {"status": "isolated"}

    # --- MAIN LOOP ---
    # Inherited from CyberAgent.engage()

if __name__ == "__main__":
    BlueDefender().engage()
