#!/usr/bin/env python3
"""
Orchestrator for the AI Cyber War Simulation.
Launches and manages Blue, Red, Green, and Purple agents.
"""
import sys
import os
import time
import subprocess
import signal
import logging
import argparse

import config
from utils import setup_logging

# Configure logging
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("Orchestrator")

AGENTS = {
    "blue": "agents/blue_brain.py",
    "red": "agents/red_brain.py",
    "green": "agents/green_brain.py",
    "purple": "agents/purple_brain.py"
}

processes = []

def signal_handler(sig, frame):
    logger.info("Shutting down simulation...")
    for p in processes:
        p.terminate()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="AI Cyber War Simulation Runner")
    parser.add_argument("--dashboard", action="store_true", help="Launch visualization dashboard")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🚀 Initializing Cyber War Simulation...")
    print("🚀 Initializing Cyber War Simulation... Press Ctrl+C to stop.")

    # Launch Agents
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"

    for name, script in AGENTS.items():
        script_path = os.path.join(config.BASE_DIR, script)
        if not os.path.exists(script_path):
            logger.error(f"Agent script not found: {script_path}")
            continue

        logger.info(f"Starting {name.capitalize()} Agent...")
        try:
            p = subprocess.Popen([sys.executable, script_path], env=env)
            processes.append(p)
        except Exception as e:
            logger.error(f"Failed to start {name}: {e}")

    # Launch Dashboard if requested
    if args.dashboard:
        dash_script = os.path.join(config.BASE_DIR, "tools/visualize_threats.py")
        if os.path.exists(dash_script):
            try:
                p = subprocess.Popen([sys.executable, dash_script], env=env)
                processes.append(p)
            except Exception as e:
                logger.error(f"Failed to start dashboard: {e}")

    # Monitor loop
    try:
        while True:
            for p in processes:
                if p.poll() is not None:
                    logger.warning(f"A subprocess (PID {p.pid}) exited unexpectedly.")
                    processes.remove(p)

            if not processes:
                logger.info("All agents have stopped.")
                break

            time.sleep(1)

    except KeyboardInterrupt:
        signal_handler(None, None)

if __name__ == "__main__":
    main()
