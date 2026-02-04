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

class CyberWarDashboard:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK) # Blue Team / Good
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)   # Red Team / Bad
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)# Warnings / Targets
        curses.init_pair(4, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Info

        self.height, self.width = stdscr.getmaxyx()
        self.alerts = []

    def load_topology(self):
        return utils.safe_json_read(config.TOPOLOGY_FILE, {})

    def load_alerts(self):
        # We don't have a centralized alert file, but we can read logs
        # or just listen to the audit log if we were fancy.
        # For now, let's just tail the blue.log for criticals
        if not os.path.exists(config.BLUE_LOG): return
        try:
            with open(config.BLUE_LOG, 'r') as f:
                lines = f.readlines()
                self.alerts = [l.strip() for l in lines if "IDS ALERT" in l or "CRITICAL" in l][-10:]
        except: pass

    def draw_box(self, y, x, h, w, title):
        self.stdscr.addstr(y, x, "┌" + "─" * (w-2) + "┐")
        self.stdscr.addstr(y, x+2, f" {title} ", curses.A_BOLD)
        for i in range(1, h-1):
            self.stdscr.addstr(y+i, x, "│")
            self.stdscr.addstr(y+i, x+w-1, "│")
        self.stdscr.addstr(y+h-1, x, "└" + "─" * (w-2) + "┘")

    def draw_nodes(self, topo):
        y_offset = 2

        # Red Nodes
        self.stdscr.addstr(y_offset, 2, "🔴 RED TEAM (Offense)", curses.color_pair(2) | curses.A_BOLD)
        r_nodes = [k for k,v in topo.items() if v.get('type') == 'RED']
        for i, node in enumerate(r_nodes):
            self.stdscr.addstr(y_offset+1+i, 4, f"• {node}")

        # Blue Nodes
        self.stdscr.addstr(y_offset, 40, "🔵 BLUE TEAM (Defense)", curses.color_pair(1) | curses.A_BOLD)
        b_nodes = [k for k,v in topo.items() if v.get('type') == 'BLUE']
        for i, node in enumerate(b_nodes):
            self.stdscr.addstr(y_offset+1+i, 42, f"• {node}")

        # Targets
        self.stdscr.addstr(y_offset+10, 20, "🎯 TARGETS (Services)", curses.color_pair(3) | curses.A_BOLD)
        self.stdscr.addstr(y_offset+11, 22, "• MockBank (10.10.10.10)")

    def draw_alerts(self):
        h = 15
        w = self.width - 4
        y = self.height - h - 2
        self.draw_box(y, 2, h, w, "🚨 LIVE IDS ALERTS")

        for i, alert in enumerate(reversed(self.alerts)):
            if i >= h-2: break
            color = curses.color_pair(2) if "CRITICAL" in alert else curses.color_pair(3)
            # Truncate to fit
            clean_alert = alert[24:] # Skip date
            self.stdscr.addstr(y+1+i, 4, clean_alert[:w-4], color)

    def draw_stats(self):
        # Read PCAP size for traffic stats
        try:
            pcap_size = os.path.getsize("logs/capture.pcap")
            self.stdscr.addstr(2, 80, f"📡 Traffic Captured: {pcap_size/1024:.2f} KB", curses.color_pair(4))
        except: pass

        # Blocked IPs (fake for now, or read from switch log if we parsed it)
        # Real integration would read switch state.
        pass

    def run(self):
        while True:
            self.stdscr.clear()
            self.stdscr.border(0)
            self.stdscr.addstr(0, 2, " 🛡️  SENTINEL CYBER WAR DASHBOARD ", curses.A_BOLD | curses.A_REVERSE)

            topo = self.load_topology()
            self.load_alerts()

            self.draw_nodes(topo)
            self.draw_alerts()
            self.draw_stats()

            self.stdscr.refresh()
            time.sleep(1)

if __name__ == "__main__":
    try:
        curses.wrapper(lambda stdscr: CyberWarDashboard(stdscr).run())
    except KeyboardInterrupt:
        pass
