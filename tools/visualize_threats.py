#!/usr/bin/env python3
"""
Dashboard for the Cyber War Simulation.
Visualizes War State, Threat Levels, and Agent Q-Values in real-time.
"""
import sys
import os
import time
import json
import shutil

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from utils import atomic_json_io

# ANSI Colors
C_RESET = "\033[0m"
C_RED = "\033[91m"
C_GREEN = "\033[92m"
C_YELLOW = "\033[93m"
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_WHITE = "\033[97m"
C_BG_RED = "\033[41m"
C_BG_BLUE = "\033[44m"

def clear_screen():
    print("\033[2J\033[H", end="")

def load_data():
    state = atomic_json_io(config.file_paths['state_file'])
    blue_q = atomic_json_io(config.file_paths['blue_q_table'])
    red_q = atomic_json_io(config.file_paths['red_q_table'])
    return state, blue_q, red_q

def draw_bar(value, max_value, length=20, color=C_GREEN):
    filled = int((value / max_value) * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"{color}{bar}{C_RESET}"

def get_top_strategies(q_table, n=3):
    if not q_table:
        return []
    # Q-Table keys are typically "State_Action"
    # We want to find the Actions with the highest average value across all states?
    # Or just the highest individual Q-values? Let's do highest Q-values.
    sorted_items = sorted(q_table.items(), key=lambda item: item[1], reverse=True)
    return sorted_items[:n]

def main():
    try:
        while True:
            state, blue_q, red_q = load_data()

            clear_screen()
            width = shutil.get_terminal_size().columns

            # Header
            print(f"{C_WHITE}{'='*width}{C_RESET}")
            print(f"{C_CYAN}🛡️  CYBER WAR SIMULATION DASHBOARD 👹{C_RESET}".center(width + 10)) # +10 for color codes
            print(f"{C_WHITE}{'='*width}{C_RESET}\n")

            # War State
            alert_level = state.get('blue_alert_level', 1)
            max_alert = config.constraints['max_alert']

            print(f"{C_WHITE}DEFCON STATUS:{C_RESET}")
            print(f"Level: {alert_level} / {max_alert}")
            print(draw_bar(alert_level, max_alert, length=40, color=C_RED if alert_level > 3 else C_GREEN))
            print("\n")

            # Agents
            col_width = width // 2

            print(f"{C_BLUE}BLUE TEAM (DEFENDER){C_RESET}".ljust(col_width) + f"{C_RED}RED TEAM (ATTACKER){C_RESET}")
            print("-" * width)

            # Stats
            blue_knowledge = len(blue_q)
            red_knowledge = len(red_q)

            print(f"Knowledge Size: {blue_knowledge:<10}".ljust(col_width) + f"Knowledge Size: {red_knowledge:<10}")
            print(f"Top Strategies:".ljust(col_width) + f"Top Strategies:")

            blue_top = get_top_strategies(blue_q)
            red_top = get_top_strategies(red_q)

            for i in range(3):
                b_str = ""
                if i < len(blue_top):
                    k, v = blue_top[i]
                    # Key is State_Action, split it. Actually format is Alert_ThreatCount_Action
                    # Just show the full key for now but truncate
                    b_str = f"{k[-20:]}: {v:.2f}"

                r_str = ""
                if i < len(red_top):
                    k, v = red_top[i]
                    r_str = f"{k[-20:]}: {v:.2f}"

                print(f"{C_BLUE}{b_str}{C_RESET}".ljust(col_width + 9) + f"{C_RED}{r_str}{C_RESET}")

            print("\n")
            print(f"{C_WHITE}Monitor: {config.file_paths['watch_dir']}{C_RESET}")
            print(f"{C_YELLOW}Press Ctrl+C to exit{C_RESET}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDashboard closed.")

if __name__ == "__main__":
    main()
