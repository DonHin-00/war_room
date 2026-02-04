#!/usr/bin/env python3
import time
import random
import os
import sys
import psutil
import json

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

logger = utils.setup_logging("ChaosMonkey", config.AUDIT_LOG)

class ChaosMonkey:
    def __init__(self):
        self.running = True

    def terminate_random_agent(self):
        """Randomly kill a process to test resilience."""
        targets = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmd = " ".join(proc.info['cmdline'] or [])
                if "red_mesh_node.py" in cmd or "blue_swarm_agent.py" in cmd:
                    targets.append(proc)
            except: pass

        if targets:
            victim = random.choice(targets)
            try:
                logger.warning(f"🐒 CHAOS: Terminating PID {victim.pid}")
                victim.kill()
            except: pass

    def corrupt_state(self):
        """Corrupt topology file to test error handling."""
        if random.random() > 0.7:
            logger.warning("🐒 CHAOS: Corrupting Topology File")
            try:
                with open(config.TOPOLOGY_FILE, 'r+') as f:
                    content = f.read()
                    if content:
                        # Flip a byte or truncate
                        f.seek(0)
                        f.write(content[:-1] + "}") # Malformed JSON
                        f.truncate()
            except: pass

    def run(self):
        print("🐒 Chaos Monkey Active. Wreaking Havoc...")
        while self.running:
            action = random.choice(["KILL", "CORRUPT", "SLEEP"])

            if action == "KILL":
                self.terminate_random_agent()
            elif action == "CORRUPT":
                self.corrupt_state()

            time.sleep(random.randint(5, 15))

if __name__ == "__main__":
    cm = ChaosMonkey()
    try:
        cm.run()
    except KeyboardInterrupt:
        pass
