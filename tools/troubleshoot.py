#!/usr/bin/env python3
"""
Deep Diagnostic & Troubleshooting Tool
Checks database integrity, process health, and logic consistency.
"""

import os
import sys
import sqlite3
import psutil
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

C_GREEN = "\033[92m"
C_RED = "\033[91m"
C_RESET = "\033[0m"

def check_db_integrity():
    print(f"[DIAG] Checking Database ({config.PATHS['DB_PATH']})...", end=" ")
    try:
        conn = sqlite3.connect(config.PATHS['DB_PATH'])
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        result = cursor.fetchone()[0]
        conn.close()

        if result == "ok":
            print(f"{C_GREEN}OK{C_RESET}")
            return True
        else:
            print(f"{C_RED}CORRUPT ({result}){C_RESET}")
            return False
    except Exception as e:
        print(f"{C_RED}ERROR ({e}){C_RESET}")
        return False

def check_zombie_processes():
    print(f"[DIAG] Checking for Zombie Agents...", end=" ")
    zombies = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmd = proc.info['cmdline']
            if cmd and ('blue_brain.py' in cmd or 'red_brain.py' in cmd):
                # Check if parent is init (1) or if it's orphaned
                if proc.ppid() == 1:
                    zombies.append(proc.pid)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    if not zombies:
        print(f"{C_GREEN}NONE{C_RESET}")
        return True
    else:
        print(f"{C_RED}FOUND {len(zombies)} (PIDs: {zombies}){C_RESET}")
        return False

def check_q_table_health():
    print(f"[DIAG] Checking Q-Table Logic...", end=" ")
    try:
        conn = sqlite3.connect(config.PATHS['DB_PATH'])
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM q_tables")
        values = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not values:
            print(f"{C_GREEN}EMPTY (OK){C_RESET}")
            return True

        # Check for NaN or Inf
        import math
        bad_vals = [v for v in values if math.isnan(v) or math.isinf(v)]
        if bad_vals:
            print(f"{C_RED}DETECTED NaN/Inf VALUES{C_RESET}")
            return False

        # Check for exploded values
        max_val = max(values)
        if max_val > 1000000:
            print(f"{C_RED}DETECTED EXPLODED VALUES (>1M){C_RESET}")
            return False

        print(f"{C_GREEN}HEALTHY (Max: {max_val:.2f}){C_RESET}")
        return True
    except Exception as e:
        print(f"{C_RED}ERROR ({e}){C_RESET}")
        return False

def run_diagnostics():
    print("=== DEEP DIAGNOSTICS ===")
    checks = [
        check_db_integrity(),
        check_zombie_processes(),
        check_q_table_health()
    ]

    if all(checks):
        print("\n[SUCCESS] System is healthy.")
    else:
        print("\n[FAILURE] Issues detected. Manual intervention required.")

if __name__ == "__main__":
    run_diagnostics()
