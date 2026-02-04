#!/usr/bin/env python3
"""
Environment Health Check
Verifies that the simulation environment is correctly set up.
"""

import os
import sys
import shutil

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

def check_python_version():
    print(f"[CHECK] Python Version: {sys.version.split()[0]}", end=" ")
    if sys.version_info < (3, 8):
        print("❌ (Requires 3.8+)")
        return False
    print("✅")
    return True

def check_directories():
    required_dirs = [
        config.PATHS['BATTLEFIELD'],
        config.PATHS['SESSIONS_DIR'],
        config.PATHS['BACKUPS']
    ]

    all_ok = True
    for d in required_dirs:
        print(f"[CHECK] Directory {os.path.basename(d)}: ", end=" ")
        if os.path.exists(d):
            if os.access(d, os.W_OK):
                print("✅")
            else:
                print("❌ (No Write Permission)")
                all_ok = False
        else:
            print("⚠️ (Created)")
            os.makedirs(d, exist_ok=True)

    return all_ok

def check_files():
    required_files = [
        "blue_brain.py",
        "red_brain.py",
        "utils.py",
        "config.py",
        "simulation_runner.py"
    ]

    base = config.PATHS['BASE_DIR']
    all_ok = True

    for f in required_files:
        path = os.path.join(base, f)
        print(f"[CHECK] File {f}: ", end=" ")
        if os.path.exists(path):
            print("✅")
        else:
            print("❌ (Missing)")
            all_ok = False
    return all_ok

def main():
    print("=== ENVIRONMENT HEALTH CHECK ===")
    checks = [
        check_python_version(),
        check_directories(),
        check_files()
    ]

    if all(checks):
        print("\n[SUCCESS] Environment is ready for war.")
        sys.exit(0)
    else:
        print("\n[FAILURE] Issues detected. Please fix them before running.")
        sys.exit(1)

if __name__ == "__main__":
    main()
