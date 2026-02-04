#!/usr/bin/env python3
"""
Chaos Monkey (Fuzzer)
Injects chaos into the live simulation to test resilience.
"""

import sys
import os
import time
import random
import string

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

def inject_noise():
    """Creates random garbage files."""
    if not os.path.exists(config.PATHS["WAR_ZONE"]): return
    name = "".join(random.choices(string.ascii_lowercase, k=8))
    path = os.path.join(config.PATHS["WAR_ZONE"], f"noise_{name}.tmp")
    with open(path, 'w') as f:
        f.write("CHAOS " * 100)
    print(f"🌪️ Injected noise: {path}")

def delete_random_state():
    """Deletes the War State file to simulate data corruption."""
    if os.path.exists(config.PATHS["WAR_STATE"]):
        try:
            os.remove(config.PATHS["WAR_STATE"])
            print("🔥 BURNED WAR STATE!")
        except: pass

def flood_attack():
    """Creates 50 threats instantly."""
    print("🌊 FLOOD ATTACK INITIATED!")
    for i in range(50):
        name = f"malware_flood_{i}.bin"
        path = os.path.join(config.PATHS["WAR_ZONE"], name)
        try:
            with open(path, 'w') as f: f.write("FLOOD")
        except: pass

def main():
    print("😈 Chaos Monkey Active. Press Ctrl+C to stop.")
    while True:
        action = random.choice(["noise", "noise", "noise", "burn", "flood"])

        if action == "noise": inject_noise()
        elif action == "burn": delete_random_state()
        elif action == "flood": flood_attack()

        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    main()
