#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Purple Team - Integrator/Balancer)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: Simulation
"""

import os
import sys
import time
import json
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
logger = logging.getLogger("PurpleBrain")
audit = AuditLogger(config.file_paths['audit_log'])

# --- VISUALS ---
C_PURPLE = "\033[95m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

@trace_errors
def engage_balance(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Purple Team AI Initialized. Role: Integrator"
    print(f"{C_PURPLE}{msg}{C_RESET}")
    logger.info(msg)

    state_file = config.file_paths['state_file']
    watch_dir = config.file_paths['watch_dir']

    # METRICS
    last_file_count = 0
    last_check_time = time.time()

    # BALANCING METRICS
    consecutive_low_alert = 0
    consecutive_high_alert = 0

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # 1. MONITOR STATE
                war_state: Dict[str, Any] = atomic_json_io(state_file)
                current_alert = war_state.get('blue_alert_level', 1)

                # 2. ADAPTIVE BALANCING
                # If alert is low for too long -> Boost Red (Simulate Zero-Day?)
                if current_alert == 1:
                    consecutive_low_alert += 1
                    consecutive_high_alert = 0
                elif current_alert == 5:
                    consecutive_high_alert += 1
                    consecutive_low_alert = 0
                else:
                    consecutive_low_alert = 0
                    consecutive_high_alert = 0

                balancing_act = ""

                if consecutive_low_alert > 5:
                    # Game is boring. Inject a conflict.
                    def stimulate_conflict(state):
                        state['blue_alert_level'] = 3
                        return state
                    atomic_json_update(state_file, stimulate_conflict)
                    balancing_act = " | ⚡ INJECTED CONFLICT (Boredom Prevention)"
                    audit.log("PURPLE", "GAME_BALANCE", {"action": "ESCALATE", "reason": "BOREDOM"})
                    consecutive_low_alert = 0

                if consecutive_high_alert > 10:
                    # Blue is overwhelmed. De-escalate.
                    def calm_down(state):
                        state['blue_alert_level'] = 3
                        return state
                    atomic_json_update(state_file, calm_down)
                    balancing_act = " | 🕊️  ENFORCED CEASEFIRE (Mercy Rule)"
                    audit.log("PURPLE", "GAME_BALANCE", {"action": "DEESCALATE", "reason": "MERCY"})
                    consecutive_high_alert = 0

                # 3. BURST DETECTION (Anomaly Detection)
                current_time = time.time()
                current_file_count = 0
                try:
                    current_file_count = len(os.listdir(watch_dir))
                except: pass

                delta_files = current_file_count - last_file_count
                delta_time = current_time - last_check_time

                # If > 5 files created per second, that's a burst!
                if delta_time > 0 and (delta_files / delta_time) > 5.0:
                    logger.warning(f"🚨 BURST DETECTED: {delta_files} files in {delta_time:.2f}s")
                    audit.log("PURPLE", "ANOMALY_DETECTED", {"type": "BURST", "rate": delta_files/delta_time})

                    # TRIGGER MAX ALERT
                    def escalation(state):
                        state['blue_alert_level'] = config.constraints['max_alert']
                        return state
                    atomic_json_update(state_file, escalation)

                last_file_count = current_file_count
                last_check_time = current_time

                log_msg = f"⚖️  Status Check: Alert Level {current_alert} | Files: {current_file_count}{balancing_act}"
                print(f"{C_PURPLE}[PURPLE AI]{C_RESET} {log_msg}")
                logger.info(log_msg)

                time.sleep(2.0) # Check every 2 seconds

            except Exception as e:
                logger.error(f"Error in Purple loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Purple Team AI Shutting Down")

if __name__ == "__main__":
    engage_balance()
