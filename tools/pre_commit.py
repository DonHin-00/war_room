#!/usr/bin/env python3
import subprocess
import sys

def run_check(command, name):
    print(f"\n--- Running {name} ---")
    # Split command for shell=False
    cmd_args = command.split()
    result = subprocess.run(cmd_args, shell=False)
    if result.returncode != 0:
        print(f"❌ {name} FAILED")
        return False
    print(f"✅ {name} PASSED")
    return True

def main():
    checks = [
        ("python3 tools/security_scan.py", "Security Scan"),
        ("python3 tools/verify_permissions.py", "Permission Check"),
    ]

    failed = False
    for cmd, name in checks:
        if not run_check(cmd, name):
            failed = True

    if failed:
        print("\n⛔ Pre-commit checks failed! Please fix the issues before committing.")
        sys.exit(1)
    else:
        print("\n🎉 All pre-commit checks passed!")
        sys.exit(0)

if __name__ == "__main__":
    main()
