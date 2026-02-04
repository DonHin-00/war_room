#!/usr/bin/env python3
"""
Orchestrator for AI Cyber War Simulation
Running Multiple Parallel Emulations (War Zones)
"""

import subprocess
import os
import time
import argparse
import signal
import sys

PROCESSES = []

def ensure_zone_directory(zone_dir):
    if not os.path.exists(zone_dir):
        os.makedirs(zone_dir)

def start_emulation(zone_id):
    """Start a pair of Red and Blue agents in a specific War Zone."""
    env = os.environ.copy()
    war_zone_name = f"war_zone_{zone_id}"
    env["WAR_ZONE_ID"] = war_zone_name

    # Ensure directory exists before starting
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zone_path = os.path.join(base_dir, war_zone_name)
    ensure_zone_directory(zone_path)

    print(f"🚀 Launching War Zone {zone_id} in {zone_path}...")

    # Redirect output to separate files for debugging
    blue_log = open(os.path.join(zone_path, "blue_stdout.log"), "w")
    red_log = open(os.path.join(zone_path, "red_stdout.log"), "w")

    # Start Blue Brain
    blue_proc = subprocess.Popen(
        ["python3", "-u", "blue_brain.py"],
        env=env,
        stdout=blue_log,
        stderr=subprocess.STDOUT
    )
    PROCESSES.append(blue_proc)

    # Start Red Brain
    red_proc = subprocess.Popen(
        ["python3", "-u", "red_brain.py"],
        env=env,
        stdout=red_log,
        stderr=subprocess.STDOUT
    )
    PROCESSES.append(red_proc)

    return blue_proc, red_proc

def cleanup(signum, frame):
    """Clean up all child processes on exit."""
    print("\n🛑 Shutting down all simulations...")
    for p in PROCESSES:
        p.terminate()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="Run parallel AI Cyber War simulations.")
    parser.add_argument("--instances", type=int, default=2, help="Number of parallel war zones to run.")
    args = parser.parse_args()

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    active_zones = []

    for i in range(1, args.instances + 1):
        blue, red = start_emulation(i)
        active_zones.append({
            "id": i,
            "blue": blue,
            "red": red
        })
        time.sleep(1) # Stagger start slightly

    print(f"✅ All {args.instances} simulations running.")
    print("Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
            # Basic Monitoring
            for zone in active_zones:
                if zone["blue"].poll() is not None:
                    print(f"⚠️ War Zone {zone['id']} Blue Team died! Exit code: {zone['blue'].returncode}")
                if zone["red"].poll() is not None:
                    print(f"⚠️ War Zone {zone['id']} Red Team died! Exit code: {zone['red'].returncode}")

    except KeyboardInterrupt:
        cleanup(None, None)

if __name__ == "__main__":
    main()
