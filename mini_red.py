#!/usr/bin/env python3
"""
Mini-Agent (Swarm) for AI Cyber War Simulation.
Designed to be spawned by Red Brain, execute a task, report back, and die.
"""

import sys
import os
import json
import time
import random
import fcntl

def safe_feedback_write(filepath, data):
    """Write feedback to a file safely using locks."""
    try:
        with open(filepath, 'w') as file:
            fcntl.flock(file, fcntl.LOCK_EX)
            json.dump(data, file)
            fcntl.flock(file, fcntl.LOCK_UN)
        return True
    except: return False

def main():
    if len(sys.argv) < 3:
        # Expected: script.py <target_dir> <feedback_file>
        sys.exit(1)

    target_dir = sys.argv[1]
    feedback_file = sys.argv[2]

    # 1. Execute Task (Aggressive Recon / Noise)
    # The swarm is "noisy" and "fast".
    impact = 0
    action = "SWARM_NOISE"

    try:
        # Create a noisy file
        noise_file = os.path.join(target_dir, f"swarm_noise_{int(time.time())}_{random.randint(1000,9999)}.tmp")
        with open(noise_file, 'w') as f:
            f.write("SWARM ATTACK " * 100)
        impact = 1

        # Simulate network activity
        time.sleep(0.5)

    except Exception as e:
        impact = -1

    # 2. Report Back
    # We report (state, action, reward, next_state) roughly
    # For simplicity, Swarm just reports a "Lesson": {action: ..., reward: ...}
    # The Main Red Brain will assimilate this.

    feedback = {
        "action": action,
        "impact": impact,
        "reward": 5 if impact > 0 else -5,
        "timestamp": time.time()
    }

    safe_feedback_write(feedback_file, feedback)

    # 3. Die (Exit)
    sys.exit(0)

if __name__ == "__main__":
    main()
