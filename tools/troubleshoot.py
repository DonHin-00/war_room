#!/usr/bin/env python3
"""
System Health Check & Diagnostic Tool
"""
import sys
import os
import importlib
import traceback

# Adjust path to find utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_file(filepath):
    exists = os.path.exists(filepath)
    print(f"[{'OK' if exists else 'MISSING'}] File: {filepath}")
    return exists

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"[OK] Import: {module_name}")
        return True
    except Exception as e:
        print(f"[FAIL] Import: {module_name} - {e}")
        return False

def main():
    print("--- STARTING SYSTEM DIAGNOSTIC ---")

    # 1. Check Directory Structure
    dirs = ["agents", "payloads", "tools"]
    for d in dirs:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), d)
        exists = os.path.exists(path)
        print(f"[{'OK' if exists else 'MISSING'}] Directory: {d}")

    # 2. Check Key Files
    files = ["utils.py", "config.py", "agents/blue_brain.py", "agents/red_brain.py", "agents/bot_brain.py", "payloads/malware.py"]
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for f in files:
        check_file(os.path.join(base, f))

    # 3. Check Imports (Simulating how agents run)
    print("\n--- CHECKING IMPORTS ---")

    # Check Utils
    if not check_import('utils'):
        print("CRITICAL: utils.py cannot be imported.")

    # Check Agents (Need to manipulate path for them)
    sys.path.append(os.path.join(base, 'agents'))

    # We can't easily import scripts that are not modules without refactoring,
    # but we can try to compile them to check syntax.
    print("\n--- SYNTAX CHECK ---")
    for f in files:
        fpath = os.path.join(base, f)
        if os.path.exists(fpath):
            try:
                with open(fpath, 'r') as source:
                    compile(source.read(), fpath, 'exec')
                print(f"[OK] Syntax: {f}")
            except Exception as e:
                print(f"[FAIL] Syntax: {f} - {e}")

    print("\n--- DIAGNOSTIC COMPLETE ---")

if __name__ == "__main__":
    main()
