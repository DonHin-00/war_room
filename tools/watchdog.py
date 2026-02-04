#!/usr/bin/env python3
"""
Daemon Watchdog
Monitors the health of Red/Blue agents via heartbeat files.
Restarts them if they flatline.
"""

import sys
import os
import time
import subprocess
import signal
import argparse

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

def start_agent(name):
    """Starts an agent process."""
    print(f"🐕 [Watchdog] Starting {name}...")
    script = f"{name}_brain.py"
    cmd = [sys.executable, script]
    # We detach slightly so we aren't parent?
    # Actually, for simulation runner integration, we might want to just report.
    # But request implies "Daemon Watchdog" that keeps things alive.

    # In this architecture, simulation_runner.py is the parent.
    # If we are a separate daemon, we need to know how to restart.
    # We will assume we are run from root dir.

    return subprocess.Popen(cmd, cwd=config.PATHS["BASE_DIR"])

def main():
    print("🐕 Daemon Watchdog Active.")

    # Track processes if we start them, but mostly we monitor files.
    # If we are strictly a monitor for an external runner, we might just log.
    # But "Daemon Watchdogs" implies active recovery.

    # Map name -> Popen object
    agents = {
        "red": None,
        "blue": None
    }

    # Initial Start
    agents["red"] = start_agent("red")
    agents["blue"] = start_agent("blue")

    try:
        while True:
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
