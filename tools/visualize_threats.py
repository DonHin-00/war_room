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
from collections import deque

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
C_PURPLE = "\033[95m"
C_CYAN = "\033[96m"
C_WHITE = "\033[97m"

def clear_screen():
    print("\033[2J\033[H", end="")

def load_data():
    state = atomic_json_io(config.file_paths['state_file'])
    blue_q = atomic_json_io(config.file_paths['blue_q_table'])
    red_q = atomic_json_io(config.file_paths['red_q_table'])
    return state, blue_q, red_q

def load_audit_logs(n=5):
    logs = []
    filepath = config.file_paths['audit_log']
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                # Use deque to efficiently get last n lines
                return list(deque(f, maxlen=n))
        except:
            return []
    return []

def draw_bar(value, max_value, length=20, color=C_GREEN):
    if max_value == 0: max_value = 1
    filled = int((value / max_value) * length)
    bar = "█" * filled + "░" * (length - filled)
    return f"{color}{bar}{C_RESET}"

def get_top_strategies(q_table, n=3):
    if not q_table:
        return []
    sorted_items = sorted(q_table.items(), key=lambda item: item[1], reverse=True)
    return sorted_items[:n]

def main():
    try:
        while True:
            state, blue_q, red_q = load_data()
            logs = load_audit_logs(5)

            clear_screen()
            width = shutil.get_terminal_size().columns

            # Header
            print(f"{C_WHITE}{'='*width}{C_RESET}")
            print(f"{C_CYAN}🛡️  CYBER WAR SIMULATION DASHBOARD 👹{C_RESET}".center(width + 10))
            print(f"{C_WHITE}{'='*width}{C_RESET}\n")

            # --- DEFCON STATUS ---
            alert_level = state.get('blue_alert_level', 1)
            max_alert = config.constraints['max_alert']

            print(f"{C_WHITE}DEFCON STATUS:{C_RESET}")
            print(f"Level: {alert_level} / {max_alert}")
            print(draw_bar(alert_level, max_alert, length=40, color=C_RED if alert_level > 3 else C_GREEN))
            print("\n")

            # --- RED TEAM CAMPAIGN ---
            campaign_phase = state.get('red_campaign_phase', 'UNKNOWN')
            campaign_idx = state.get('red_campaign_index', 0)
            campaign_total = state.get('red_campaign_total', 5)

            print(f"{C_RED}RED TEAM CAMPAIGN STATUS:{C_RESET}")
            print(f"Phase: {campaign_phase} ({campaign_idx + 1}/{campaign_total})")
            print(draw_bar(campaign_idx + 1, campaign_total, length=40, color=C_PURPLE))
            print("\n")

            # --- AGENT STATS ---
            col_width = width // 2

            print(f"{C_BLUE}BLUE TEAM (DEFENDER){C_RESET}".ljust(col_width) + f"{C_RED}RED TEAM (ATTACKER){C_RESET}")
            print("-" * width)

            blue_top = get_top_strategies(blue_q)
            red_top = get_top_strategies(red_q)

            for i in range(3):
                b_str = ""
                if i < len(blue_top):
                    k, v = blue_top[i]
                    b_str = f"{k[-25:]}: {v:.2f}"

                r_str = ""
                if i < len(red_top):
                    k, v = red_top[i]
                    r_str = f"{k[-25:]}: {v:.2f}"

                print(f"{C_BLUE}{b_str}{C_RESET}".ljust(col_width + 9) + f"{C_RED}{r_str}{C_RESET}")

            print("\n")

            # --- RECENT EVENTS ---
            print(f"{C_WHITE}RECENT EVENTS:{C_RESET}")
            print("-" * width)
            for line in logs:
                try:
                    entry = json.loads(line)
                    ts = time.strftime('%H:%M:%S', time.localtime(entry.get('timestamp', 0)))
                    agent = entry.get('agent', 'UNK')
                    event = entry.get('event', 'UNK')
                    color = C_BLUE if agent == "BLUE" else C_RED if agent == "RED" else C_PURPLE
                    print(f"{C_WHITE}[{ts}]{C_RESET} {color}{agent:<8}{C_RESET} | {event} | {entry.get('details', {})}")
                except:
                    print(line.strip())

            print("\n")
            print(f"{C_YELLOW}Press Ctrl+C to exit{C_RESET}")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDashboard closed.")

if __name__ == "__main__":
    main()
