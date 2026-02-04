#!/usr/bin/env python3
import sys
import os
import platform

def check_environment():
    print("🌍 Checking Environment...")

    # Check Python Version
    req_version = (3, 8)
    cur_version = sys.version_info
    if cur_version < req_version:
        print(f"❌ Python version too old: {platform.python_version()}. Need 3.8+")
        sys.exit(1)
    print(f"✅ Python Version: {platform.python_version()}")

    # Check Directories
    dirs = ["simulation_data", "logs", "models"]
    for d in dirs:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d)
        if os.path.exists(path):
            print(f"✅ Directory exists: {d}")
        else:
            print(f"⚠️  Directory missing: {d} (Will be created on run)")

    # Check Permissions (Simulated)
    if hasattr(os, 'getuid'):
        if os.getuid() == 0:
            print("❌ Running as ROOT is unsafe!")
            sys.exit(1)
        print(f"✅ Running as UID: {os.getuid()}")

    print("✅ Environment Check Passed")

if __name__ == "__main__":
    check_environment()
