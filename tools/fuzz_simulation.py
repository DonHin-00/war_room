#!/usr/bin/env python3
"""
Chaos Fuzzer
Injects corruption and random data to test simulation robustness.
"""

import os
import sys
import random
import time
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import utils

def fuzz_state_file():
    target = config.PATHS['STATE_FILE']
    if not os.path.exists(target):
        return

    print(f"[FUZZ] Corrupting {target}...")
    try:
        # 1. Random Truncation
        if random.random() < 0.5:
            with open(target, 'r+') as f:
                content = f.read()
                f.seek(0)
                f.truncate()
                f.write(content[:len(content)//2])

        # 2. JSON Injection
        else:
            with open(target, 'w') as f:
                f.write('{"blue_alert_level": "INVALID_INT", "garbage": true}')

    except Exception as e:
        print(f"[FUZZ] Error fuzzing state: {e}")

def fuzz_battlefield():
    target_dir = config.PATHS['BATTLEFIELD']
    if not os.path.exists(target_dir):
        return

    print(f"[FUZZ] Littering battlefield...")
    # Create weird files
    for i in range(5):
        fname = os.path.join(target_dir, f"fuzz_{random.randint(0, 9999)}.tmp")
        with open(fname, 'wb') as f:
            f.write(os.urandom(1024))

def run_fuzzer():
    print("=== CHAOS FUZZER STARTED ===")
    while True:
        action = random.choice([fuzz_state_file, fuzz_battlefield])
        action()
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    try:
        run_fuzzer()
    except KeyboardInterrupt:
        print("\n[FUZZ] Stopping...")
