#!/usr/bin/env python3
"""
Fuzzing tool for the Cyber War Simulation.
Injects chaos: malformed files, corrupted JSON state, and random signals.
"""
import sys
import os
import time
import random
import string
import logging

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils import safe_file_write

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [CHAOS] - %(message)s',
    datefmt='%H:%M:%S'
)

def random_string(length=100):
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))

def create_malformed_threat(watch_dir):
    """Creates a threat file with weird names or content."""
    name_types = [
        f"malware_{int(time.time())}.exe",
        f".sys_{int(time.time())}.dat",
        f"malware_{random_string(10)}.tmp",
        f"weird_file_no_prefix_{int(time.time())}.txt",
        f"malware_unicode_🚀_{int(time.time())}.bin"
    ]

    filename = random.choice(name_types)
    filepath = os.path.join(watch_dir, filename)

    content = random.choice([
        os.urandom(1024), # Random binary
        random_string(5000).encode('utf-8'), # Random text
        b"\x00" * 1000, # Null bytes
    ])

    try:
        with open(filepath, 'wb') as f:
            f.write(content)
        logging.info(f"💉 Injected threat: {filename}")
    except Exception as e:
        logging.error(f"Failed to inject threat: {e}")

def corrupt_state_file(state_file):
    """Attempts to corrupt the war_state.json file (atomic_json_io should handle this)."""
    if random.random() > 0.8: # 20% chance
        try:
            # Write garbage directly, bypassing locks (simulating external process crash/corruption)
            # Actually, let's use the safe writer to be 'polite' about our chaos,
            # but write invalid JSON.
            # safe_file_write handles locking, so this tests the parser's robustness.
            invalid_json = "{'broken': key, " + random_string(20)
            safe_file_write(state_file, invalid_json)
            logging.info(f"🔨 Corrupted state file: {state_file}")
        except Exception as e:
            logging.error(f"Failed to corrupt state: {e}")

def main():
    watch_dir = config.file_paths['watch_dir']
    state_file = config.file_paths['state_file']

    logging.info("🔥 Chaos Monkey started. Press Ctrl+C to stop.")

    try:
        while True:
            action = random.choice(['threat', 'threat', 'threat', 'corrupt'])

            if action == 'threat':
                create_malformed_threat(watch_dir)
            elif action == 'corrupt':
                corrupt_state_file(state_file)

            time.sleep(random.uniform(0.1, 2.0))

    except KeyboardInterrupt:
        logging.info("Chaos Monkey stopped.")

if __name__ == "__main__":
    main()
