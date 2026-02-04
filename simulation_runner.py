#!/usr/bin/env python3
"""
War Room Orchestrator
Runs the AI Cyber War Simulation (Blue vs Red) in a controlled environment.
"""

import subprocess
import time
import os
import signal
import sys
import argparse
import config
import shutil

# --- UTILS ---
def clean_battlefield():
    """Wipes the war zone."""
    if os.path.exists(config.PATHS["WAR_ZONE"]):
        shutil.rmtree(config.PATHS["WAR_ZONE"])
    os.makedirs(config.PATHS["WAR_ZONE"], exist_ok=True, mode=0o700)

def reset_memory():
    """Wipes Q-Tables and State."""
    if os.path.exists(config.PATHS["Q_TABLE_RED"]): os.remove(config.PATHS["Q_TABLE_RED"])
    if os.path.exists(config.PATHS["Q_TABLE_BLUE"]): os.remove(config.PATHS["Q_TABLE_BLUE"])
    if os.path.exists(config.PATHS["WAR_STATE"]): os.remove(config.PATHS["WAR_STATE"])
    if os.path.exists(config.PATHS["SIGNATURES"]): os.remove(config.PATHS["SIGNATURES"])

# --- MAIN RUNNER ---
def run_simulation(duration=60, reset=False):
    print(f"🚀 Initializing War Room Simulation...")

    if reset:
        print("🧹 Resetting Memory and State...")
        reset_memory()

    clean_battlefield()

    # Start Agents
    print("🔵 Deploying Blue Team (Sentinel)...")
    blue_proc = subprocess.Popen([sys.executable, "blue_brain.py"],
                                 cwd=config.PATHS["BASE_DIR"])

    print("🔴 Deploying Red Team (Predator)...")
    red_proc = subprocess.Popen([sys.executable, "red_brain.py"],
                                cwd=config.PATHS["BASE_DIR"])

    print(f"⏱️  Simulation Active for {duration} seconds. Press Ctrl+C to abort.")

    start_time = time.time()
    try:
        while (time.time() - start_time) < duration:
            # Monitor health
            if blue_proc.poll() is not None:
                print("⚠️  Blue Team crashed! Restarting...")
                blue_proc = subprocess.Popen([sys.executable, "blue_brain.py"], cwd=config.PATHS["BASE_DIR"])

            if red_proc.poll() is not None:
                print("⚠️  Red Team crashed! Restarting...")
                red_proc = subprocess.Popen([sys.executable, "red_brain.py"], cwd=config.PATHS["BASE_DIR"])

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Simulation Aborted by User.")
    finally:
        print("🛑 Terminating Agents...")
        blue_proc.send_signal(signal.SIGINT)
        red_proc.send_signal(signal.SIGINT)

        # Give them time to save memory
        time.sleep(2)

        if blue_proc.poll() is None: blue_proc.kill()
        if red_proc.poll() is None: red_proc.kill()

        print("✅ Simulation Complete.")
        print(f"📂 Artifacts located in: {config.PATHS['WAR_ZONE']}")
        print(f"📝 Logs: {config.PATHS['LOG_BLUE']}, {config.PATHS['LOG_RED']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Cyber War Orchestrator")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--reset", action="store_true", help="Reset AI memory before starting")
    args = parser.parse_args()

    run_simulation(duration=args.duration, reset=args.reset)
