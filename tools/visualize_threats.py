
import sys
import os
import time
import json
import sqlite3

# Add parent dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

def clear_screen():
    print("\033[2J\033[H", end="")

def load_db_state():
    try:
        conn = sqlite3.connect("simulation.db")
        cursor = conn.cursor()

        # Get State
        cursor.execute("SELECT value FROM war_state WHERE key='blue_alert_level'")
        row = cursor.fetchone()
        alert = json.loads(row[0]) if row else 1

        # Get Threat Stats
        cursor.execute("SELECT type, COUNT(*) FROM threat_intel GROUP BY type")
        intel_stats = dict(cursor.fetchall())

        # Get Exp Replay
        cursor.execute("SELECT COUNT(*) FROM experience_replay")
        xp_count = cursor.fetchone()[0]

        conn.close()
        return alert, intel_stats, xp_count
    except:
        return 1, {}, 0

def scan_battlefield():
    files = []
    try:
        with os.scandir(config.TARGET_DIR) as entries:
            for entry in entries:
                files.append(entry.name)
    except: pass
    return files

def draw_dashboard():
    while True:
        clear_screen()
        alert, intel, xp = load_db_state()
        files = scan_battlefield()

        # Header
        print(f"\033[1;37;44m AI CYBER WAR - WAR ROOM CONSOLE \033[0m")
        print(f"Time: {time.strftime('%H:%M:%S')}\n")

        # Status
        color = ["\033[92m", "\033[92m", "\033[93m", "\033[91m", "\033[91;5m"][min(4, alert-1)]
        print(f"DEFCON: {color}LEVEL {alert}\033[0m")
        print(f"Intelligence: {intel.get('hash', 0)} Hashes | {intel.get('filename', 0)} Filenames")
        print(f"Experience: {xp} events learned")
        print("-" * 40)

        # Battlefield Map (ASCII)
        print("BATTLEFIELD SECTOR MAP:")
        # Simple visualization: 10 files per line
        icons = {
            ".sh": "📜",
            ".bin": "💣",
            ".exe": "👾",
            ".enc": "🔒",
            ".log": "📝",
            ".sys": "👻"
        }

        buffer = ""
        for i, f in enumerate(files):
            ext = os.path.splitext(f)[1]
            if f.startswith(".sys"): ext = ".sys"
            icon = icons.get(ext, "📄")
            buffer += f"{icon} "
            if (i + 1) % 10 == 0:
                buffer += "\n"
        print(buffer)
        print("-" * 40)

        # Recent Logs (Tail)
        print("LIVE FEED:")
        try:
            with open(os.path.join(config.LOG_DIR, "blue.log"), "r") as f:
                lines = f.readlines()[-5:]
                for line in lines:
                    print(f"\033[94m[BLUE]\033[0m {line.strip()}")
        except: pass

        time.sleep(1)

if __name__ == "__main__":
    try:
        draw_dashboard()
    except KeyboardInterrupt:
        print("\nConsole Closed.")
