#!/usr/bin/env python3
import curses
import time
import json
import os
import sys
import threading
import requests

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

def get_edr_logs():
    """Tail blue log."""
    if os.path.exists(config.BLUE_LOG):
        try:
            with open(config.BLUE_LOG, 'r') as f:
                return f.readlines()[-10:]
        except: pass
    return []

def get_red_logs():
    """Tail red log."""
    if os.path.exists(config.RED_LOG):
        try:
            with open(config.RED_LOG, 'r') as f:
                return f.readlines()[-10:]
        except: pass
    return []

def get_alerts():
    """Tail ALERTS.txt."""
    if os.path.exists("ALERTS.txt"):
        try:
            with open("ALERTS.txt", 'r') as f:
                return f.readlines()[-5:]
        except: pass
    return []

def draw_dashboard(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(500)

    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE) # Blue Team
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)  # Red Team
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_CYAN) # Header

    while True:
        stdscr.clear()
        h, w = stdscr.getmaxyx()

        # Header
        title = "⚔️  LIVE FIRE EXERCISE: BATTLE FOR LOCALHOST  ⚔️"
        stdscr.addstr(0, 0, title.center(w), curses.color_pair(3))

        # --- LEFT: BLUE TEAM (DEFENSE) ---
        stdscr.addstr(2, 2, "[ BLUE TEAM - EDR STATUS ]", curses.color_pair(1))
        blue_logs = get_edr_logs()
        for i, line in enumerate(blue_logs):
            if 4+i < h-2:
                stdscr.addstr(4+i, 2, line.strip()[:w//2-4])

        # --- RIGHT: RED TEAM (OFFENSE) ---
        col_red = w // 2
        stdscr.addstr(2, col_red, "[ RED TEAM - MESH STATUS ]", curses.color_pair(2))
        red_logs = get_red_logs()
        for i, line in enumerate(red_logs):
            if 4+i < h-2:
                stdscr.addstr(4+i, col_red, line.strip()[:w//2-4])

        # --- OVERLAY: THE MATRIX (Network Graph) ---
        # Simulating a visual graph in the center
        center_y = h // 2
        center_x = w // 2

        # ASCII Mesh
        graph = [
            "   (R1) <---> (R2)   ",
            "    ^          ^     ",
            "    |          |     ",
            "   (B1) <---> (B2)   "
        ]

        for i, row in enumerate(graph):
            try:
                stdscr.addstr(center_y - 2 + i, center_x - 10, row, curses.A_BOLD)
            except: pass

        # Separator
        for y in range(2, h-8):
            try: stdscr.addch(y, w//2 - 1, '|')
            except: pass

        # --- BOTTOM: HIGH PRIORITY ALERTS ---
        stdscr.addstr(h-8, 2, "[ 🚨 INTRUSION ALERTS 🚨 ]", curses.color_pair(2) | curses.A_BLINK)
        stdscr.hline(h-7, 0, curses.ACS_HLINE, w)

        alerts = get_alerts()
        for i, line in enumerate(alerts):
            if h-6+i < h-1:
                stdscr.addstr(h-6+i, 2, line.strip()[:w-4], curses.color_pair(2))

        # Status Bar
        stdscr.addstr(h-1, 0, f"Time: {time.strftime('%H:%M:%S')} | Press 'q' to Quit", curses.A_REVERSE)

        c = stdscr.getch()
        if c == ord('q'):
            break

if __name__ == "__main__":
    curses.wrapper(draw_dashboard)
