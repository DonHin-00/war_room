#!/usr/bin/env python3
import sys
import os
import time
import subprocess
import signal

# Add root to path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

def run_emulation(duration=60):
    print("🚀 INITIALIZING CYBER WARFARE EMULATION ENVIRONMENT")
    print("==================================================")

    procs = []
    env = os.environ.copy()
    env["PYTHONPATH"] = ROOT_DIR

    # 1. Start Virtual Switch
    print("[*] Starting Virtual Network Switch...")
    # Kill existing switch if any
    try:
        subprocess.run(["fuser", "-k", "10000/tcp"], stderr=subprocess.DEVNULL)
    except: pass
    time.sleep(1)

    # Run as module to allow relative imports
    p_switch = subprocess.Popen([sys.executable, "-m", "vnet.switch"], cwd=ROOT_DIR, env=env)
    procs.append(p_switch)
    time.sleep(2) # Wait for switch to bind

    # 2. Start Services
    print("[*] Starting Mock Banking Service (Target)...")
    p_bank = subprocess.Popen([sys.executable, "services/mock_bank.py"], cwd=ROOT_DIR, env=env)
    procs.append(p_bank)
    time.sleep(1)

    # 3. Start Blue Team (Defense)
    print("[*] Deploying Blue Swarm (3 Nodes)...")
    for _ in range(3):
        p = subprocess.Popen([sys.executable, "agents/blue_brain.py"], cwd=ROOT_DIR, env=env)
        procs.append(p)

    # 4. Start Red Team (Offense)
    print("[*] Deploying Red Mesh (3 Nodes)...")
    for _ in range(3):
        p = subprocess.Popen([sys.executable, "agents/red_brain.py"], cwd=ROOT_DIR, env=env)
        procs.append(p)

    # 5. Start Rainbow Teams (Support)
    print("[*] Deploying Rainbow Support Teams (Yellow, Orange, Green, White)...")
    teams = [
        "agents/yellow_brain.py",
        "agents/orange_brain.py",
        "agents/green_brain.py",
        "agents/white_brain.py",
        "purple_auditor.py"
    ]
    for script in teams:
        p = subprocess.Popen([sys.executable, script], cwd=ROOT_DIR, env=env)
        procs.append(p)

    print(f"\n✅ EMULATION LIVE. Running for {duration} seconds...")
    try:
        time.sleep(duration)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n🛑 SHUTTING DOWN EMULATION...")
        for p in procs:
            if p.poll() is None:
                p.terminate()

        # Give them time to die
        time.sleep(1)

        for p in procs:
            if p.poll() is None:
                p.kill()

        print("✅ Shutdown Complete.")

if __name__ == "__main__":
    run_emulation()
