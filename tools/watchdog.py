#!/usr/bin/env python3
"""
Daemon Watchdog
Monitors the health of Red/Blue agents via heartbeat files.
Restarts them if they flatline.
Includes Auto-Fix logic for stale artifacts.
"""

import sys
import os
import time
import subprocess
import signal
import argparse
import glob

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

HEARTBEAT_TIMEOUT = 5.0 # Seconds before declaring dead

def check_heartbeat(agent_name):
    """Checks if the agent's heartbeat file is fresh."""
    hb_file = os.path.join(config.PATHS["DATA_DIR"], f"{agent_name}.heartbeat")
    if not os.path.exists(hb_file):
        return False
    try:
        mtime = os.stat(hb_file).st_mtime
        if time.time() - mtime > HEARTBEAT_TIMEOUT:
            return False
    except: return False
    return True

def clean_stale_locks():
    """Auto-Fix: Removes stale temporary files that might be locking system."""
    # Look for temp files in battlefield or data dir that are old
    try:
        now = time.time()
        # Clean temp files created by safe_file_write that might have been left over
        # They usually are in the target directory with a random name
        # We can't easily distinguish valid temp files from stale ones unless by age.
        # Let's say > 10 seconds is stale for an atomic write.

        # Check DATA_DIR for tmp files
        for tmp in glob.glob(os.path.join(config.PATHS["DATA_DIR"], "*.tmp")):
            try:
                if now - os.stat(tmp).st_mtime > 10:
                    os.remove(tmp)
                    print(f"🧹 [Watchdog] Removed stale temp file: {tmp}")
            except: pass

        # Check WAR_ZONE
        for tmp in glob.glob(os.path.join(config.PATHS["WAR_ZONE"], "*.tmp")):
             try:
                if now - os.stat(tmp).st_mtime > 10:
                    os.remove(tmp)
                    # print(f"🧹 [Watchdog] Removed stale war zone temp: {tmp}")
             except: pass

    except Exception as e:
        print(f"⚠️ [Watchdog] Cleanup Error: {e}")

def start_agent(name):
    """Starts an agent process."""
    print(f"🐕 [Watchdog] Starting {name}...")
    script = f"{name}_brain.py"
    cmd = [sys.executable, script]
    return subprocess.Popen(cmd, cwd=config.PATHS["BASE_DIR"])

def main():
    print("🐕 Daemon Watchdog Active.")

    agents = {
        "red": None,
        "blue": None
    }

    # Initial Start
    agents["red"] = start_agent("red")
    agents["blue"] = start_agent("blue")

    try:
        while True:
            # 0. Maintenance
            clean_stale_locks()

            for name, proc in agents.items():
                # 1. Check Process Status
                if proc.poll() is not None:
                    print(f"🐕 [Watchdog] {name} process died (Exit Code: {proc.returncode}). Restarting...")
                    agents[name] = start_agent(name)
                    continue

                # 2. Check Heartbeat (Liveness)
                if not check_heartbeat(name):
                    print(f"🐕 [Watchdog] {name} flatlined (Heartbeat Stale). Killing & Restarting...")
                    try:
                        os.kill(proc.pid, signal.SIGKILL)
                    except: pass
                    agents[name] = start_agent(name)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n🐕 [Watchdog] Terminating agents...")
        for proc in agents.values():
            if proc:
                proc.send_signal(signal.SIGINT)
                try: proc.wait(timeout=2)
                except: proc.kill()

if __name__ == "__main__":
    main()
