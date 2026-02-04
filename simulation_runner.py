#!/usr/bin/env python3
"""
War Room Orchestrator
Runs the AI Cyber War Simulation (Blue vs Red) in a controlled environment.
Now with Watchdog integration for resilience.
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

    # Start Agents directly via Watchdog or alongside it?
    # Requirement: "Integrate Watchdog... Spawn watchdog alongside agents."
    # AND "Watchdog... monitors... restarts"
    # So Simulation Runner spawns Watchdog, Watchdog spawns/manages Agents.
    # OR Simulation Runner spawns everything and Watchdog monitors.
    # The watchdog script I wrote spawns agents. So Runner just needs to spawn Watchdog.

    print("🐕 Deploying Daemon Watchdog (Manager)...")
    watchdog_proc = subprocess.Popen([sys.executable, "tools/watchdog.py"],
                                     cwd=config.PATHS["BASE_DIR"])

    print(f"⏱️  Simulation Active for {duration} seconds. Press Ctrl+C to abort.")

    start_time = time.time()
    try:
        while (time.time() - start_time) < duration:
            if watchdog_proc.poll() is not None:
                print("⚠️  Watchdog crashed! Restarting system...")
                watchdog_proc = subprocess.Popen([sys.executable, "tools/watchdog.py"],
                                                 cwd=config.PATHS["BASE_DIR"])
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Simulation Aborted by User.")
    finally:
        print("🛑 Terminating Simulation...")
        # Killing Watchdog should trigger its cleanup (it traps SIGINT)
        watchdog_proc.send_signal(signal.SIGINT)
        try:
            watchdog_proc.wait(timeout=5)
        except:
            watchdog_proc.kill()

        # Ensure agents are dead if Watchdog failed to kill them
        # (Cleanup is good practice)
        os.system("pkill -f red_brain.py")
        os.system("pkill -f blue_brain.py")

        print("✅ Simulation Complete.")
        print(f"📂 Artifacts located in: {config.PATHS['WAR_ZONE']}")
        print(f"📝 Logs: {config.PATHS['LOG_BLUE']}, {config.PATHS['LOG_RED']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Cyber War Orchestrator")
    parser.add_argument("--duration", type=int, default=60, help="Duration in seconds")
    parser.add_argument("--reset", action="store_true", help="Reset AI memory before starting")
    args = parser.parse_args()

    run_simulation(duration=args.duration, reset=args.reset)
