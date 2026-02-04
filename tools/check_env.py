#!/usr/bin/env python3
"""
Environment Sanity Checker
Verifies system readiness for the simulation.
"""

import sys
import os
import shutil

def check_python_version():
    v = sys.version_info
    if v.major < 3 or (v.major == 3 and v.minor < 8):
        print("❌ Python 3.8+ required.")
        return False
    print("✅ Python Version OK.")
    return True

def check_permissions():
    try:
        test_file = ".perm_test"
        with open(test_file, 'w') as f: f.write("test")
        os.chmod(test_file, 0o600)
        os.remove(test_file)
        print("✅ File Permissions OK.")
        return True
    except Exception as e:
        print(f"❌ Permission Check Failed: {e}")
        return False

def check_disk_space():
    try:
        total, used, free = shutil.disk_usage(".")
        if free < 100 * 1024 * 1024: # 100MB
            print("❌ Low Disk Space (<100MB).")
            return False
        print(f"✅ Disk Space OK ({free // (1024*1024)}MB free).")
        return True
    except:
        return True # Skip if unsupported

def main():
    print("🔍 Running Environment Checks...")
    if all([check_python_version(), check_permissions(), check_disk_space()]):
        print("🚀 System Ready.")
        sys.exit(0)
    else:
        print("🛑 System Check Failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
