#!/usr/bin/env python3
"""
War Room Orchestrator
Runs the AI Cyber War Simulation (Blue vs Red) in a 4-Layer Segregated SOC.
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
    """Wipes the war zone and recreates the 4-layer architecture."""
    if os.path.exists(config.PATHS["WAR_ZONE"]):
        shutil.rmtree(config.PATHS["WAR_ZONE"])

    os.makedirs(config.PATHS["WAR_ZONE"], exist_ok=True, mode=0o700)

    # Create Segregated Zones
    for zone_name, zone_path in config.ZONES.items():
        os.makedirs(zone_path, exist_ok=True, mode=0o700)
        # Create dummy assets
        with open(os.path.join(zone_path, "readme.txt"), 'w') as f:
            f.write(f"Welcome to {zone_name} Zone")

        # Create sensitive assets (Loot for Red Team)
        if zone_name in ["SERVER", "CORE"]:
            with open(os.path.join(zone_path, "db_config.json"), 'w') as f:
                f.write('{"db_host": "localhost", "db_pass": "super_secret_password"}')
            with open(os.path.join(zone_path, "shadow.bak"), 'wb') as f:
                f.write(os.urandom(64)) # Simulated hash dump

        if zone_name == "USER":
            with open(os.path.join(zone_path, "passwords.txt"), 'w') as f:
                f.write("admin:hunter2\nroot:toor")

    # Create Proc Dir if not exists
    if os.path.exists(config.PATHS["PROC"]):
        shutil.rmtree(config.PATHS["PROC"])
    os.makedirs(config.PATHS["PROC"], exist_ok=True, mode=0o700)

def reset_memory():
    """Wipes Q-Tables and State."""
    if os.path.exists(config.PATHS["Q_TABLE_RED"]): os.remove(config.PATHS["Q_TABLE_RED"])
    if os.path.exists(config.PATHS["Q_TABLE_BLUE"]): os.remove(config.PATHS["Q_TABLE_BLUE"])
    if os.path.exists(config.PATHS["WAR_STATE"]): os.remove(config.PATHS["WAR_STATE"])
    if os.path.exists(config.PATHS["SIGNATURES"]): os.remove(config.PATHS["SIGNATURES"])

# --- MAIN RUNNER ---
def run_simulation(duration=60, reset=False):
    print(f"🚀 Initializing 4-Layer SOC Simulation...")

    if reset:
        print("🧹 Resetting Memory and State...")
        reset_memory()

    clean_battlefield()

    # Start C2 Server
    print("💀 Starting C2 Server (Infrastructure)...")
    c2_proc = subprocess.Popen([sys.executable, "tools/c2_server.py"],
                                     cwd=config.PATHS["BASE_DIR"],
                                     stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL)

    time.sleep(1) # Allow C2 to bind

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
        watchdog_proc.send_signal(signal.SIGINT)
        c2_proc.terminate()

        try:
            watchdog_proc.wait(timeout=5)
            c2_proc.wait(timeout=2)
        except:
            watchdog_proc.kill()
            c2_proc.kill()

        # Cleanup child agents
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
