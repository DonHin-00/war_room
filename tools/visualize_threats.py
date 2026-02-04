#!/usr/bin/env python3
"""
War Room Dashboard
Real-time TUI for monitoring the Cyber War Simulation.
"""

import sys
import os
import time
import json
import curses

# Add parent to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def load_audit_tail(n=10):
    events = []
    if not os.path.exists(config.PATHS["AUDIT_LOG"]): return events
    try:
        with open(config.PATHS["AUDIT_LOG"], 'r') as f:
            lines = f.readlines()
            for line in lines[-n:]:
                try: events.append(json.loads(line))
                except: pass
    except: pass
    return events

def get_threat_counts():
    counts = {"Encrypted": 0, "Rootkits": 0, "Beacons": 0, "Malware": 0}
    if not os.path.exists(config.PATHS["WAR_ZONE"]): return counts
    try:
        with os.scandir(config.PATHS["WAR_ZONE"]) as it:
            for entry in it:
                if entry.name.endswith(".enc"): counts["Encrypted"] += 1
                elif ".sys" in entry.name: counts["Rootkits"] += 1
                elif "beacon" in entry.name: counts["Beacons"] += 1
                elif "malware" in entry.name: counts["Malware"] += 1
    except: pass
    return counts

def draw_dashboard(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)

    while True:
        stdscr.clear()

        # Header
        stdscr.addstr(0, 0, "🚀 WAR ROOM LIVE OPS DASHBOARD", curses.A_BOLD)
        stdscr.addstr(1, 0, "="*40)

        # Stats
        counts = get_threat_counts()
        row = 3
        stdscr.addstr(row, 0, "📊 THREAT INTELLIGENCE:")
        stdscr.addstr(row+1, 2, f"🦠 Malware:   {counts['Malware']}")
        stdscr.addstr(row+2, 2, f"💀 Rootkits:  {counts['Rootkits']}")
        stdscr.addstr(row+3, 2, f"🔒 Encrypted: {counts['Encrypted']}")
        stdscr.addstr(row+4, 2, f"📡 Beacons:   {counts['Beacons']}")

        # Recent Events
        row += 7
        stdscr.addstr(row, 0, "📜 LIVE EVENT STREAM:")
        events = load_audit_tail(10)
        for i, event in enumerate(reversed(events)):
            ts = time.strftime('%H:%M:%S', time.localtime(event['timestamp']))
            actor = event['actor']
            etype = event['type']
            color = curses.color_pair(1) if actor == "RED" else curses.color_pair(2)
            stdscr.addstr(row+1+i, 2, f"[{ts}] {actor} :: {etype}", color)

        stdscr.refresh()

        c = stdscr.getch()
        if c == ord('q'):
            break

def main():
    try:
        curses.wrapper(draw_dashboard)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    # Setup simple colors if possible
    # Note: color_pair needs init_pair in wrapper
    def wrapped(stdscr):
        if curses.has_colors():
            curses.start_color()
            curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
            curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)
        draw_dashboard(stdscr)

    curses.wrapper(wrapped)
