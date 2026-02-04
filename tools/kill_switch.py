#!/usr/bin/env python3
import psutil
import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def kill_all():
    print("☠️  SENTINEL KILL SWITCH ACTIVATED ☠️")

    targets = ["red_mesh_node.py", "blue_swarm_agent.py", "purple_auditor.py"]
    killed = 0

    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = " ".join(proc.info['cmdline'] or [])
            for t in targets:
                if t in cmd:
                    print(f"Terminating {t} (PID {proc.info['pid']})...")
                    proc.kill()
                    killed += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    print(f"✅ Neutralized {killed} processes.")

if __name__ == "__main__":
    kill_all()
