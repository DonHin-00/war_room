#!/usr/bin/env python3
import curses
import time
import json
import os
import sys

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

def draw_dashboard(stdscr):
    # Setup
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000) # Refresh every 1s

    # Colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Header
        title = "🛡️ SENTINEL CYBER RANGE DASHBOARD 🛡️"
        stdscr.addstr(0, max(0, (w-len(title))//2), title, curses.A_BOLD | curses.A_UNDERLINE)

        # --- LEFT PANEL: STATUS ---
        stdscr.addstr(2, 2, "[ SYSTEM STATUS ]", curses.color_pair(3))

        # Read War State
        war_state = utils.safe_json_read(config.STATE_FILE, {})
        alert_lvl = war_state.get('blue_alert_level', 1)

        defcon = config.DEFCON_LEVELS.get(6 - alert_lvl, "UNKNOWN") # Map 1->5 to Defcon logic?
        # Actually logic is confusing. Let's just print Alert Level.

        stdscr.addstr(4, 2, f"Alert Level: {alert_lvl}/5")
        bar = "█" * alert_lvl + "░" * (5-alert_lvl)
        color = curses.color_pair(2) if alert_lvl > 3 else curses.color_pair(3)
        stdscr.addstr(4, 20, bar, color)

        # Read Stats from Logs (Approximation)
        # In real app we'd tail properly. Here we just grab size or last few lines.

        # --- MIDDLE PANEL: THREATS ---
        stdscr.addstr(2, 40, "[ ACTIVE THREATS ]", curses.color_pair(2))

        try:
            files = os.listdir(config.SIMULATION_DATA_DIR)
            malware = [f for f in files if "malware" in f or ".sys" in f or ".enc" in f]
            honeypots = [f for f in files if f in config.HONEYPOT_NAMES]

            stdscr.addstr(4, 40, f"Malware Detected: {len(malware)}")
            stdscr.addstr(5, 40, f"Active Honeypots: {len(honeypots)}")

            # List some files
            for i, f in enumerate(malware[:5]):
                stdscr.addstr(7+i, 40, f"- {f[:30]}", curses.color_pair(2))
        except:
            stdscr.addstr(4, 40, "Error reading threat data", curses.color_pair(2))

        # --- RIGHT PANEL: NETWORK ---
        stdscr.addstr(2, 80, "[ NETWORK BUS ]", curses.color_pair(4))
        try:
            packets = os.listdir(config.NETWORK_BUS_DIR)
            stdscr.addstr(4, 80, f"Packets in Transit: {len(packets)}")
        except: pass

        # --- BOTTOM PANEL: AUDIT STREAM ---
        stdscr.addstr(15, 2, "[ LIVE AUDIT STREAM ]", curses.color_pair(1))
        stdscr.hline(16, 2, curses.ACS_HLINE, w-4)

        try:
            if os.path.exists(config.AUDIT_LOG):
                with open(config.AUDIT_LOG, 'r') as f:
                    lines = f.readlines()
                    last_lines = lines[-10:] # Last 10
                    for i, line in enumerate(last_lines):
                        try:
                            data = json.loads(line)
                            ts = time.strftime('%H:%M:%S', time.localtime(data['timestamp']))
                            agent = data['agent']
                            event = data['event']

                            c = curses.color_pair(1)
                            if agent == "RED": c = curses.color_pair(2)

                            row_str = f"{ts} | {agent:<5} | {event:<20} | {str(data.get('details',''))[:50]}"
                            stdscr.addstr(17+i, 2, row_str, c)
                        except: pass
        except: pass

        # Footer
        stdscr.addstr(h-2, 2, "Press 'q' to quit", curses.A_DIM)

        # Input
        c = stdscr.getch()
        if c == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(draw_dashboard)
