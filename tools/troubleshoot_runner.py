#!/usr/bin/env python3
"""
Troubleshoot/Chaos Runner for the Simulation.
Injects faults to verify resilience.
"""

import subprocess
import time
import os
import signal
import sys
import shutil
import random

def inject_chaos(war_zone_dir):
    time.sleep(5)
    print("\n[CHAOS] Injecting Faults...")

    # 1. Corrupt State File
    state_file = "war_state.json"
    if os.path.exists(state_file):
        print("[CHAOS] Corrupting war_state.json")
        with open(state_file, "w") as f:
            f.write("{ INVALID JSON ...") # Truncated/Garbage

    time.sleep(2)

    # 2. Kill Random Malware PIDs directly (bypassing Blue)
    try:
        pids = subprocess.check_output(["pgrep", "-f", "payloads/malware.py"], text=True).splitlines()
        if pids:
            victim = random.choice(pids)
            print(f"[CHAOS] kill -9 {victim}")
            os.kill(int(victim), signal.SIGKILL)
    except: pass

    time.sleep(5)
    print("[CHAOS] Injection Complete.")

def main():
    print("Starting Chaos Simulation...")

    # Clean previous run
    war_zone_dir = os.path.abspath("war_zone")
    if os.path.exists(war_zone_dir): shutil.rmtree(war_zone_dir)
    os.makedirs(war_zone_dir)

    # Env
    env = os.environ.copy()
    env["WAR_ZONE_DIR"] = war_zone_dir

    # Launch Bots
    blue = subprocess.Popen([sys.executable, "-u", "blue_brain.py"], env=env)
    red = subprocess.Popen([sys.executable, "-u", "red_brain.py"], env=env)

    try:
        inject_chaos(war_zone_dir)

        # Check if bots survived
        if blue.poll() is not None:
            print("Blue Brain DIED!")
        else:
            print("Blue Brain SURVIVED.")

        if red.poll() is not None:
            print("Red Brain DIED!")
        else:
            print("Red Brain SURVIVED.")

    except KeyboardInterrupt:
        pass
    finally:
        blue.terminate()
        red.terminate()
        shutil.rmtree(war_zone_dir)

if __name__ == "__main__":
    main()
