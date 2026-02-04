#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Green Team - Users)
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
def engage_work(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Green Team AI Initialized. Role: Civilian User"
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
                # 1. WORK (Create Files)
                if random.random() < 0.3: # 30% chance to create a file
                    filename = f"user_doc_{int(time.time())}_{random.randint(1000,9999)}.txt"
                    filepath = os.path.join(watch_dir, filename)
                    try:
                        with open(filepath, 'w') as f:
                            f.write("Important business document content.\n" * random.randint(1, 10))
                        logger.info(f"Created benign file: {filename}")
                    except Exception:
                        pass

                # 2. INSIDER THREAT (Accidental Click)
                if random.random() < 0.05: # 5% chance to be risky
                    try:
                        with os.scandir(watch_dir) as it:
                            for entry in it:
                                if entry.is_file() and entry.name.startswith("malware_"):
                                    new_name = f"invoice_{int(time.time())}.exe"
                                    new_path = os.path.join(watch_dir, new_name)
                                    os.rename(entry.path, new_path)
                                    logger.warning(f"⚠️  User clicked malware! Renamed {entry.name} -> {new_name}")
                                    audit.log("GREEN", "INSIDER_MISTAKE", {"original": entry.name, "new": new_name})
                                    break
                    except Exception:
                        pass

                # 3. SHADOW IT (Unsanctioned Tools)
                # Creates executable-looking files that aren't malware but distract Blue
                if random.random() < 0.05:
                    tool_name = f"game_crack_{random.randint(100,999)}.exe"
                    filepath = os.path.join(watch_dir, tool_name)
                    try:
                        with open(filepath, 'wb') as f:
                            f.write(os.urandom(512)) # Random binary data
                        logger.info(f"💾 User installed Shadow IT: {tool_name}")
                        audit.log("GREEN", "SHADOW_IT_INSTALL", {"file": tool_name})
                    except Exception:
                        pass

                # 4. SECURITY AWARENESS (User Self-Defense)
                # Users occasionally spot obvious malware and delete it themselves
                if random.random() < 0.1:
                    try:
                        with os.scandir(watch_dir) as it:
                            for entry in it:
                                if entry.is_file() and (entry.name.startswith("malware_") or entry.name.endswith(".exe")):
                                    # Users act on suspicion
                                    if random.random() < 0.5:
                                        os.remove(entry.path)
                                        logger.info(f"🛡️ User deleted suspicious file: {entry.name}")
                                        audit.log("GREEN", "USER_DEFENSE", {"file": entry.name})
                                        break
                    except Exception:
                        pass

                # 5. CLEANUP (Delete old files)
                if random.random() < 0.1:
                    try:
                        with os.scandir(watch_dir) as it:
                            for entry in it:
                                if entry.is_file() and entry.name.startswith("user_doc_"):
                                    if random.random() < 0.2:
                                        os.remove(entry.path)
                                        break
                    except Exception:
                        pass

                time.sleep(random.uniform(1.0, 3.0))

            except Exception as e:
                logger.error(f"Error in Green loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Green Team AI Shutting Down")

if __name__ == "__main__":
    engage_work()
