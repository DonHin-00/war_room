#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Green Team - Automation & Integration)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: Simulation
"""

import os
import sys
import time
import random
import logging
from typing import Optional, List, Dict, Any

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    atomic_json_io,
    atomic_json_update,
    setup_logging,
    AuditLogger
)
from utils.trace_logger import trace_errors
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("GreenBrain")
audit = AuditLogger(config.file_paths['audit_log'])

# --- VISUALS ---
C_GREEN = "\033[92m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

@trace_errors
def engage_automation(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Green Team AI Initialized. Role: Automation & Remediation"
    print(f"{C_GREEN}{msg}{C_RESET}")
    logger.info(msg)

    watch_dir = config.file_paths['watch_dir']

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # 1. AUTO-REMEDIATION (Improving MTTR)
                # Check for indicators of compromise that Blue might have missed or that need cleanup
                remediated = 0

                # Check for Ransom Notes and auto-restore (simulated)
                # Red Team now uses "READ_ME.txt"
                ransom_note = os.path.join(watch_dir, "READ_ME.txt")
                if os.path.exists(ransom_note):
                    logger.info("♻️  Green Team executing Playbook: RANSOMWARE_RECOVERY")
                    try:
                        os.remove(ransom_note)
                        remediated += 1
                        audit.log("GREEN", "PLAYBOOK_EXECUTION", {"name": "Ransomware Cleanup"})

                        # Simulate restoring files (just creating a 'restored' file)
                        with open(os.path.join(watch_dir, f"restored_data_{int(time.time())}.bak"), 'w') as f:
                            f.write("Restored critical data.")
                    except: pass

                # Check for ".enc" files (Ransomware artifacts) and "quarantine" them
                try:
                    with os.scandir(watch_dir) as it:
                        for entry in it:
                            if entry.is_file() and entry.name.endswith(".enc"):
                                # Automate moving to quarantine (delete for sim)
                                try:
                                    os.remove(entry.path)
                                    remediated += 1
                                    logger.info(f"♻️  Green Team Quarantined: {entry.name}")
                                except: pass
                except: pass

                if remediated > 0:
                    print(f"{C_GREEN}[GREEN AI]{C_RESET} ♻️  Remediated {remediated} incidents (Automation)")

                # 2. CONFIGURATION MANAGEMENT
                # Ensure critical config files exist (Self-Healing Infrastructure)
                critical_configs = ["system_config.ini", "network_policy.yaml"]
                for conf in critical_configs:
                    path = os.path.join(watch_dir, conf)
                    if not os.path.exists(path):
                        try:
                            with open(path, 'w') as f: f.write("secure=true")
                            logger.info(f"🔧 Green Team Restored Configuration: {conf}")
                        except: pass

                time.sleep(2.0) # Automation runs periodically

            except Exception as e:
                logger.error(f"Error in Green loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Green Team AI Shutting Down")

if __name__ == "__main__":
    engage_automation()
