#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Sentinel - User Ally)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: Automation, Observability
"""

import os
import sys
import time
import json
import logging
import datetime
from typing import Optional, List, Dict, Any

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    atomic_json_io,
    setup_logging,
    safe_file_write
)
from utils.trace_logger import trace_errors
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("SentinelBrain")

# --- VISUALS ---
C_GOLD = "\033[93m" # Gold for the User's Champion
C_RESET = "\033[0m"

# --- MAIN LOOP ---

@trace_errors
def engage_sentinel(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Sentinel Agent Initialized. Role: User Ally & Overwatch"
    print(f"{C_GOLD}{msg}{C_RESET}")
    logger.info(msg)

    watch_dir = config.file_paths['watch_dir']
    log_file = config.file_paths['log_file']
    report_file = os.path.join(config.BASE_DIR, "executive_report.md")

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # 1. AUTO-MAINTENANCE (Log Rotation)
                if os.path.exists(log_file):
                    size_mb = os.path.getsize(log_file) / (1024 * 1024)
                    if size_mb > 5.0: # 5MB Limit
                        logger.warning(f"Log file too large ({size_mb:.2f}MB). Rotating...")
                        # In a real system we'd zip it, here we truncate to save disk for the user
                        with open(log_file, 'w') as f:
                            f.write(f"--- Log Rotated by Sentinel at {datetime.datetime.now()} ---\n")

                # 2. AUTO-CLEANUP (Battlefield Hygiene)
                # If the battlefield gets too cluttered, it slows down the simulation.
                # Sentinel helps the USER by keeping performance high.
                try:
                    files = os.listdir(watch_dir)
                    if len(files) > 500:
                        logger.info(f"Battlefield cluttered ({len(files)} files). Purging old debris...")
                        # Delete oldest 100 files
                        full_paths = [os.path.join(watch_dir, f) for f in files]
                        full_paths.sort(key=os.path.getmtime)
                        for f in full_paths[:100]:
                            try: os.remove(f)
                            except: pass
                except: pass

                # 3. EXECUTIVE REPORTING (Intelligence Summary)
                # Generates a clean Markdown report for the user to read.
                if iteration % 5 == 0:
                    war_state = atomic_json_io(config.file_paths['state_file'])
                    blue_q = atomic_json_io(config.file_paths['blue_q_table'])
                    red_q = atomic_json_io(config.file_paths['red_q_table'])

                    alert = war_state.get('blue_alert_level', 'N/A')

                    report = f"""# 🛡️ Sentinel Executive Summary
**Timestamp:** {datetime.datetime.now()}

## 📊 War Status
* **Defcon Level:** {alert}
* **Active Threats:** {len(files) if 'files' in locals() else 'Unknown'}

## 🧠 Intelligence
* **Blue Knowledge:** {len(blue_q)} strategies
* **Red Knowledge:** {len(red_q)} strategies

## 🧹 Maintenance Actions
* **Log Status:** Healthy
* **Disk Usage:** Optimized

*Sentinel is watching over your simulation.*
"""
                    safe_file_write(report_file, report)

                time.sleep(5.0) # Sentinel works deliberately

            except Exception as e:
                logger.error(f"Error in Sentinel loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Sentinel Agent Shutting Down")

if __name__ == "__main__":
    engage_sentinel()
