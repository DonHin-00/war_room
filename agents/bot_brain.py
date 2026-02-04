#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Bot - Force Multiplier)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: Automation
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
    setup_logging
)
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("BotBrain")

# --- VISUALS ---
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_force(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Bot Agent Initialized. Role: Force Multiplier"
    print(f"{C_YELLOW}{msg}{C_RESET}")
    logger.info(msg)

    watch_dir = config.file_paths['watch_dir']
    state_file = config.file_paths['state_file']

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # 1. READ STATE
                war_state: Dict[str, Any] = atomic_json_io(state_file)
                alert_level = war_state.get('blue_alert_level', 1)

                # 2. DECIDE ALLEGIANCE
                # High Alert -> Help Blue (Rapid Defense)
                # Low Alert -> Help Red (Rapid Offense)

                if alert_level >= 3:
                    # MODE: RAPID DEFENSE (Help Blue)
                    cleaned = 0
                    try:
                        with os.scandir(watch_dir) as it:
                            for entry in it:
                                if entry.is_file() and entry.name.startswith("malware_"):
                                    # Bot uses "dumb" signature match (prefix) but runs fast
                                    try:
                                        os.remove(entry.path)
                                        cleaned += 1
                                    except: pass
                    except: pass

                    if cleaned > 0:
                        log_msg = f"⚡ Force Multiplier (BLUE): Purged {cleaned} threats"
                        print(f"{C_YELLOW}[BOT AI]{C_RESET} {log_msg}")
                        logger.info(log_msg)

                else:
                    # MODE: RAPID OFFENSE (Help Red)
                    # Create noise/chaff to confuse Blue or speed up Red's goal
                    created = 0
                    for _ in range(3): # Burst of 3
                        fname = os.path.join(watch_dir, f"malware_noise_{int(time.time())}_{random.randint(100,999)}.tmp")
                        try:
                            with open(fname, 'w') as f: f.write("NOISE")
                            created += 1
                        except: pass

                    if created > 0:
                        log_msg = f"⚡ Force Multiplier (RED): Generated {created} noise files"
                        print(f"{C_YELLOW}[BOT AI]{C_RESET} {log_msg}")
                        logger.info(log_msg)

                # Bot runs faster than main brains
                time.sleep(random.uniform(0.5, 1.0))

            except Exception as e:
                logger.error(f"Error in Bot loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Bot Agent Shutting Down")

if __name__ == "__main__":
    engage_force()
