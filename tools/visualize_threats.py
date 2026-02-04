#!/usr/bin/env python3
"""
Threat Visualization Tool
Generates a real-time dashboard of the cyber war.
"""

import os
import sys
import json
import time

# Add parent directory to path to import utils/config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
import utils

C_RED = "\033[91m"
C_BLUE = "\033[94m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_RESET = "\033[0m"
C_BOLD = "\033[1m"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_status():
    war_state = utils.safe_json_read(config.PATHS['STATE_FILE'])
    alert_level = war_state.get('blue_alert_level', 1)

    battlefield = config.PATHS['BATTLEFIELD']
    files = []
    try:
        files = os.listdir(battlefield)
    except: pass

    malware_count = len([f for f in files if f.startswith('malware_')])
    rootkit_count = len([f for f in files if f.startswith('.sys_')])

    return alert_level, malware_count, rootkit_count, files

def draw_dashboard():
    alert_level, malware, rootkits, files = get_status()

    clear_screen()
    print(f"{C_BOLD}=== CYBER WAR DASHBOARD ==={C_RESET}")
    print(f"Time: {time.strftime('%H:%M:%S')}")

    # Alert Level Bar
    bar = "█" * alert_level + "░" * (5 - alert_level)
    color = C_GREEN if alert_level < 3 else (C_YELLOW if alert_level < 5 else C_RED)
    print(f"\nDEFCON Level: [{color}{bar}{C_RESET}] ({alert_level}/5)")

    # Stats
    print(f"\n{C_RED}Active Threats:{C_RESET}")
    print(f"  Malware (Visible): {C_RED}{malware}{C_RESET}")
    print(f"  Rootkits (Hidden): {C_RED}{rootkits}{C_RESET}")

    # Battlefield Visualization
    print(f"\n{C_BLUE}Battlefield Map:{C_RESET}")
    if not files:
        print("  [ Empty - System Clean ]")
    else:
        grid = []
        for i, f in enumerate(files):
            if f.startswith('malware_'):
                icon = "🦠"
            elif f.startswith('.sys_'):
                icon = "💀"
            else:
                icon = "📄"
            grid.append(icon)

        # Print grid 10 wide
        for i in range(0, len(grid), 10):
            print("  " + " ".join(grid[i:i+10]))

if __name__ == "__main__":
    while True:
        draw_dashboard()
        time.sleep(1)
