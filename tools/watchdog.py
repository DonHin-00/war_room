#!/usr/bin/env python3
"""
Real-time filesystem watchdog for the Cyber War Simulation.
Monitors the battlefield directory and logs events.
"""
import sys
import os
import time
import logging
from typing import Dict

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [WATCHDOG] - %(message)s',
    datefmt='%H:%M:%S'
)

def monitor_directory(path: str, poll_interval: float = 0.5):
    """
    Monitors a directory for file creations and deletions using polling.
    (Simple polling implementation to avoid external dependencies like 'watchdog')
    """
    logging.info(f"Monitoring battlefield: {path}")

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError:
            logging.error(f"Could not create directory: {path}")
            return

    # Initial state
    known_files: Dict[str, float] = {}
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    known_files[entry.name] = entry.stat().st_mtime
    except FileNotFoundError:
        pass

    try:
        while True:
            current_files = {}
            try:
                with os.scandir(path) as it:
                    for entry in it:
                        if entry.is_file():
                            current_files[entry.name] = entry.stat().st_mtime
            except FileNotFoundError:
                logging.warning(f"Directory {path} disappeared!")
                known_files = {}
                time.sleep(poll_interval)
                continue

            # Check for new files
            for filename, mtime in current_files.items():
                if filename not in known_files:
                    logging.info(f"➕ CREATED: {filename}")
                elif mtime != known_files[filename]:
                    logging.info(f"📝 MODIFIED: {filename}")

            # Check for deleted files
            for filename in known_files:
                if filename not in current_files:
                    logging.info(f"❌ DELETED: {filename}")

            known_files = current_files
            time.sleep(poll_interval)

    except KeyboardInterrupt:
        logging.info("Watchdog stopped.")

if __name__ == "__main__":
    monitor_directory(config.file_paths['watch_dir'])
