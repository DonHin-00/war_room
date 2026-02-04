#!/usr/bin/env python3
import curses
import time
import json
import os
import sys
import threading

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

        # Dynamic ASCII Mesh
        topo = utils.safe_json_read(config.TOPOLOGY_FILE, {})

        red_nodes = [v for k,v in topo.items() if v['type'] == 'RED']
        blue_nodes = [v for k,v in topo.items() if v['type'] == 'BLUE']

        # --- LEFT PANEL: EVOLUTION MONITOR ---
        # Calculate Average Genes
        avg_jitter = 0
        avg_aggro = 0
        stealth_count = 0

        if red_nodes:
            for r in red_nodes:
                genes = r.get('genes', {})
                avg_jitter += genes.get('jitter', 0)
                avg_aggro += genes.get('aggression', 0)
                if genes.get('stealth'): stealth_count += 1

            avg_jitter /= len(red_nodes)
            avg_aggro /= len(red_nodes)
            stealth_pct = (stealth_count / len(red_nodes)) * 100

            stdscr.addstr(2, 2, "[ EVOLUTIONARY METRICS ]", curses.color_pair(2))
            stdscr.addstr(4, 2, f"Avg Jitter: {avg_jitter:.2f}s")
            stdscr.addstr(5, 2, f"Avg Aggro:  {avg_aggro:.2f}")
            stdscr.addstr(6, 2, f"Stealth %:  {stealth_pct:.1f}%")

            # Meta Analysis
            meta = "BALANCED"
            if avg_aggro > 0.8: meta = "ZERG RUSH"
            if stealth_pct > 80: meta = "NINJA"
            stdscr.addstr(8, 2, f"META: {meta}", curses.A_BLINK)

        # --- BRAIN ACTIVITY ---
        stdscr.addstr(10, 2, "[ MACHINE LEARNING METRICS ]", curses.color_pair(4))

        # Read Model Stats
        try:
            model_files = os.listdir(config.MODELS_DIR)
            total_size = sum([os.path.getsize(os.path.join(config.MODELS_DIR, f)) for f in model_files])
            model_count = len(model_files)

            stdscr.addstr(11, 2, f"Active Models: {model_count}")
            stdscr.addstr(12, 2, f"Knowledge Base: {total_size} bytes")
            stdscr.addstr(13, 2, "Federated Sync: ACTIVE")
        except:
            stdscr.addstr(11, 2, "ML Status: INITIALIZING...")

        # Simple Circle Layout
        try:
            # Red Line (Show Node IDs)
            # red_nodes is a list of dicts now, need keys?
            # We need to restructure how we read topo to get IDs.
            # Reread strictly for IDs or just use the dicts if they had ID inside.
            # They don't have ID inside value.

            red_ids = [k for k,v in topo.items() if v['type'] == 'RED']
            blue_ids = [k for k,v in topo.items() if v['type'] == 'BLUE']

            red_str = " <-> ".join([f"(R:{n[:4]})" for n in red_ids[:3]])
            stdscr.addstr(center_y - 2, max(0, center_x - len(red_str)//2), red_str, curses.color_pair(2))

            # Vs
            stdscr.addstr(center_y, center_x - 2, " VS ", curses.A_BOLD)

            # Blue Line
            blue_str = " <-> ".join([f"(B:{n[:4]})" for n in blue_ids[:3]])
            stdscr.addstr(center_y + 2, max(0, center_x - len(blue_str)//2), blue_str, curses.color_pair(1))

            if len(red_ids) > 3 or len(blue_ids) > 3:
                stdscr.addstr(center_y + 4, center_x - 10, f"+ {len(red_ids)-3} Red, {len(blue_ids)-3} Blue hidden")

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
