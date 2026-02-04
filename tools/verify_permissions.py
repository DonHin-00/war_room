#!/usr/bin/env python3
import os
import stat
import sys

def check_permissions():
    print("🛡️ Sentinel Permission Check Initiated...")

    critical_dirs = {
        "simulation_data": 0o700
    }

    critical_files = {
        "config.py": 0o600,
        "blue_brain.py": 0o700, # executable
        "red_brain.py": 0o700,  # executable
    }

    failed = False

    # Check directories
    for d, mode in critical_dirs.items():
        if os.path.exists(d):
            current_mode = stat.S_IMODE(os.stat(d).st_mode)
            if current_mode != mode:
                # Be a bit lenient, just warn if too open (e.g. world writable)
                if current_mode & 0o002: # World writable
                    print(f"❌ Directory {d} is world-writable ({oct(current_mode)})!")
                    failed = True
                elif current_mode & 0o020: # Group writable
                     print(f"⚠️ Directory {d} is group-writable ({oct(current_mode)}). Should be {oct(mode)}.")
                else:
                    print(f"✅ Directory {d} permissions OK.")
        else:
             print(f"⚠️ Directory {d} does not exist (will be created by app).")

    # Check files
    for f, mode in critical_files.items():
        if os.path.exists(f):
            current_mode = stat.S_IMODE(os.stat(f).st_mode)
             # Check for world writable
            if current_mode & 0o002:
                print(f"❌ File {f} is world-writable!")
                failed = True
            else:
                print(f"✅ File {f} permissions OK.")
        else:
             print(f"⚠️ File {f} does not exist.")

    if failed:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    check_permissions()
