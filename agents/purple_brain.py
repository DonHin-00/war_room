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
    setup_logging
)
import config

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("PurpleBrain")

# --- VISUALS ---
C_PURPLE = "\033[95m"
C_RESET = "\033[0m"

# --- MAIN LOOP ---

def engage_balance(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Purple Team AI Initialized. Role: Integrator"
    print(f"{C_PURPLE}{msg}{C_RESET}")
    logger.info(msg)

    state_file = config.file_paths['state_file']

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1

            try:
                # 1. MONITOR
                war_state: Dict[str, Any] = atomic_json_io(state_file)
                current_alert = war_state.get('blue_alert_level', 1)

                # 2. BALANCE
                # If alert level is too high, maybe suppress it slightly to allow Red to try again?
                # Or if too low, inject a simulation event?

                # Simple logic: If alert stays at MAX for too long, reset it to give Red a chance?
                # This logic would require tracking history, but for now let's just log stats.

                log_msg = f"⚖️  Status Check: Alert Level {current_alert}"
                print(f"{C_PURPLE}[PURPLE AI]{C_RESET} {log_msg}")
                logger.info(log_msg)

                # 3. INTEGRATION (Metric Aggregation could go here)
                # For now, we just ensure the game keeps flowing.

                time.sleep(5.0) # Integrator checks less frequently

            except Exception as e:
                logger.error(f"Error in Purple loop: {e}")
                time.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Purple Team AI Shutting Down")

if __name__ == "__main__":
    engage_balance()
