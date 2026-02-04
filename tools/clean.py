#!/usr/bin/env python3
"""
Cleaner Script
Wipes all simulation artifacts to reset the environment.
"""

import os
import shutil
import sys

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def clean_artifacts():
    print("🧹 Cleaning Simulation Artifacts...")

    dirs_to_clean = [
        config.PATHS["WAR_ZONE"],
        config.PATHS["DATA_DIR"],
        os.path.join(config.PATHS["BASE_DIR"], "__pycache__"),
        os.path.join(config.PATHS["BASE_DIR"], "tests", "__pycache__"),
        os.path.join(config.PATHS["BASE_DIR"], "tools", "__pycache__")
    ]

    files_to_clean = [
        config.PATHS["LOG_RED"],
        config.PATHS["LOG_BLUE"],
        config.PATHS["LOG_MAIN"]
    ]

    for d in dirs_to_clean:
        if os.path.exists(d):
            try:
                shutil.rmtree(d)
                print(f"   Deleted directory: {d}")
            except Exception as e:
                print(f"   Failed to delete {d}: {e}")

    for f in files_to_clean:
        if os.path.exists(f):
            try:
                os.remove(f)
                print(f"   Deleted file: {f}")
            except Exception as e:
                print(f"   Failed to delete {f}: {e}")

    # Also look for .proc if it leaked
    proc_dir = os.path.join(config.PATHS["BASE_DIR"], ".proc")
    if os.path.exists(proc_dir):
        shutil.rmtree(proc_dir)
        print(f"   Deleted leaked .proc: {proc_dir}")

    print("✨ Environment Cleaned.")

if __name__ == "__main__":
    clean_artifacts()
