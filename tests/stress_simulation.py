#!/usr/bin/env python3
"""
Heavy Stress Test for Cyber War Simulation
Orchestrates agents, injects chaos, and validates resilience.
"""

import os
import sys
import time
import subprocess
import threading
import random
import shutil
import signal

# Configuration
DURATION = 45 # Seconds
AGENTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents")
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
if not os.path.exists(LOG_DIR): os.mkdir(LOG_DIR)

class StressTest:
    def __init__(self):
        self.processes = []
        self.running = True

    def clean_environment(self):
        print("[*] Cleaning battlefield...")
        target_dir = "/tmp"
        for f in os.listdir(target_dir):
            if f.startswith(("malware_", "system_log_", "PASTE_", "EXFIL_", "RANSOM_")) or f.endswith(".enc"):
                try: os.remove(os.path.join(target_dir, f))
                except: pass

        # Reset State (Optional, but good for clean test)
        # for f in ["war_state.json", "blue_q_table.json", "red_q_table.json", "gatekeeper.json"]:
        #     if os.path.exists(f): os.remove(f)

    def start_agent(self, name, script):
        print(f"[*] Starting Agent: {name}")
        cmd = [sys.executable, "-u", os.path.join(AGENTS_DIR, script)]
        # Redirect output to separate log files in LOG_DIR
        with open(os.path.join(LOG_DIR, f"{name.lower()}.log"), "w") as out:
            p = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT)
            self.processes.append(p)

    def chaos_monkey(self):
        """Simulates random user activity and noise."""
        print("[*] Unleashing Chaos Monkey...")
        while self.running:
            try:
                action = random.choice(["create", "delete", "touch"])
                fname = os.path.join("/tmp", f"user_doc_{random.randint(1,100)}.txt")

                if action == "create":
                    with open(fname, "w") as f: f.write("Important business data " * 10)
                elif action == "delete":
                    if os.path.exists(fname): os.remove(fname)
                elif action == "touch":
                    if os.path.exists(fname): os.utime(fname, None)

                time.sleep(random.uniform(0.1, 0.5))
            except: pass

    def run(self):
        self.clean_environment()

        # Launch Agents
        self.start_agent("Blue", "blue_brain.py")
        self.start_agent("Red", "red_brain.py")
        self.start_agent("Bot", "bot_brain.py")

        # Start Chaos
        chaos_thread = threading.Thread(target=self.chaos_monkey)
        chaos_thread.start()

        print(f"[*] Simulation running for {DURATION} seconds...")
        try:
            time.sleep(DURATION)
        except KeyboardInterrupt:
            print("\n[!] Interrupted!")

        self.running = False
        print("[*] Stopping Agents...")
        for p in self.processes:
            p.send_signal(signal.SIGTERM)

        time.sleep(2) # Allow grace period
        for p in self.processes:
            if p.poll() is None:
                p.kill()

        chaos_thread.join()
        self.analyze_results()

    def analyze_results(self):
        print("\n--- TEST ANALYSIS ---")

        # Check logs for keywords
        stats = {
            "Blue Mitigations": 0,
            "Red Impacts": 0,
            "WAF Bans": 0,
            "Errors": 0
        }

        for name in ["blue.log", "red.log", "bot.log"]:
            log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), name)
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    content = f.read()
                    stats["Blue Mitigations"] += content.count("Kill: ")
                    stats["Red Impacts"] += content.count("Impact: ")
                    stats["WAF Bans"] += content.count("Engaging Shadow Ban")
                    stats["Errors"] += content.count("ERROR")
                    stats["Errors"] += content.count("Traceback")

        print(f"Stats: {stats}")

        if stats["Errors"] > 0:
            print("[FAIL] Errors detected in logs!")
            sys.exit(1)
        elif stats["Blue Mitigations"] == 0 and stats["Red Impacts"] == 0:
            print("[WARN] Low activity detected.")
        else:
            print("[PASS] System is active and stable.")

if __name__ == "__main__":
    test = StressTest()
    test.run()
