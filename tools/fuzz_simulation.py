#!/usr/bin/env python3
import sys
import os
import json
import random
import string
import time

# Add root to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils
import config

def fuzz_string(length=100):
    """Generate random garbage string."""
    return ''.join(random.choices(string.printable, k=length))

def fuzz_state():
    """Inject garbage into war_state.json."""
    print("⚡ Fuzzing war_state.json...")

    # 1. Invalid JSON
    utils.safe_file_write(config.STATE_FILE, "{ broken json")

    # 2. Valid JSON, Invalid Schema
    bad_state = {
        "blue_alert_level": "High", # Should be int
        "timestamp": "Now"          # Should be float
    }
    utils.safe_json_write(config.STATE_FILE, bad_state)

    # 3. Valid Schema, Logic Violation
    logic_error = {
        "blue_alert_level": 9999, # Out of bounds
        "timestamp": time.time()
    }
    utils.safe_json_write(config.STATE_FILE, logic_error)

def fuzz_q_table(filepath):
    """Corrupt Q-Tables."""
    print(f"⚡ Fuzzing {filepath}...")
    utils.safe_file_write(filepath, fuzz_string(1024))

def fuzz_simulation_data():
    """Create malformed files in simulation_data."""
    print("⚡ Fuzzing simulation_data/...")
    target = os.path.join(config.SIMULATION_DATA_DIR, "malware_fuzz.bin")

    # Extremely long filename
    try:
        long_name = os.path.join(config.SIMULATION_DATA_DIR, "A" * 255)
        utils.secure_create(long_name, "test")
    except: pass

    # Symlink Attack Attempt (Should be blocked by utils)
    try:
        symlink_target = os.path.join(config.SIMULATION_DATA_DIR, "fake_link")
        os.symlink("/etc/passwd", symlink_target)
    except: pass

def main():
    print("🛡️ Sentinel Fuzz Test Initiated 🛡️")

    # Ensure dirs exist
    if not os.path.exists(config.SIMULATION_DATA_DIR):
        os.makedirs(config.SIMULATION_DATA_DIR)

    fuzz_state()
    fuzz_q_table(config.Q_TABLE_BLUE)
    fuzz_simulation_data()

    print("\n✅ Fuzzing Complete. Check logs for crashes (there should be none, handled by utils).")

    # Clean up
    try:
        if os.path.exists(config.STATE_FILE): os.remove(config.STATE_FILE)
    except: pass

if __name__ == "__main__":
    main()
