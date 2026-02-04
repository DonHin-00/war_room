#!/usr/bin/env python3
"""
Real-time ASCII Dashboard for the War Room
Run this in a separate terminal during simulation.
"""

import os
import sys
import time
import json
import glob

# Add parent dir to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import utils

def clear_screen():
    print("\033[H\033[J", end="")

def load_json(filepath):
    return utils.access_memory(filepath) or {}

def main():
    print("Initializing Dashboard...")
    while True:
        try:
            clear_screen()

            # Load State
            war_state = load_json(config.STATE_FILE)
            alert_level = war_state.get('blue_alert_level', 1)

            # Scan War Zone
            files = []
            if os.path.exists(config.WAR_ZONE_DIR):
                files = os.listdir(config.WAR_ZONE_DIR)

            malware = [f for f in files if "malware" in f and not f.endswith(".enc")]
            hidden = [f for f in files if f.startswith(".sys")]
            beacons = [f for f in files if f.endswith(".c2_beacon")]
            encrypted = [f for f in files if f.endswith(".enc")]
            honeypots = [f for f in files if f.endswith(".honey")]
            tarpits = [f for f in files if f.endswith(".tar_pit")]
            startups = [f for f in files if f.startswith(".startup")]

            # Load Stats (Q-Tables)
            red_q = load_json(config.Q_TABLE_RED)
            blue_q = load_json(config.Q_TABLE_BLUE)

            # --- HEADER ---
            print(f"╔{'═'*60}╗")
            print(f"║ {'AI CYBER WARFARE SIMULATION - LIVE DASHBOARD':^58} ║")
            print(f"╠{'═'*60}╣")

            # --- ALERT STATUS ---
            color = "\033[92m" if alert_level < 3 else ("\033[93m" if alert_level < 5 else "\033[91m")
            print(f"║ DEFCON LEVEL: {color}{alert_level}{'\033[0m'} {'█'*alert_level}{' '*(5-alert_level)} {' ' * 38}║")

            # --- THREAT MATRIX ---
            print(f"╠{'═'*60}╣")
            print(f"║ {'THREAT MATRIX':^58} ║")
            print(f"╠{'─'*60}╣")
            print(f"║ Active Malware   : {len(malware):<3} 🦠 {' ' * 38}║")
            print(f"║ Hidden Rootkits  : {len(hidden):<3} 👻 {' ' * 38}║")
            print(f"║ C2 Beacons       : {len(beacons):<3} 📡 {' ' * 38}║")
            print(f"║ Encrypted Files  : {len(encrypted):<3} 🔒 {' ' * 38}║")
            print(f"║ Persistence      : {len(startups):<3} 💾 {' ' * 38}║")

            # --- DEFENSIVE ASSETS ---
            print(f"╠{'─'*60}╣")
            print(f"║ {'DEFENSIVE ASSETS & HEALTH':^58} ║")
            print(f"╠{'─'*60}╣")
            print(f"║ Honey Tokens     : {len(honeypots):<3} 🍯 {' ' * 38}║")
            print(f"║ Tar Pits         : {len(tarpits):<3} 🕸️ {' ' * 38}║")

            # Check critical files
            crit_ok = 0
            if os.path.exists(config.CRITICAL_DIR):
                crit_ok = len(os.listdir(config.CRITICAL_DIR))
            print(f"║ Critical Files   : {crit_ok:<3} 🛡️ {' ' * 38}║")

            # --- INTELLIGENCE ---
            print(f"╠{'═'*60}╣")
            print(f"║ {'INTELLIGENCE':^58} ║")
            print(f"╠{'─'*60}╣")
            blue_knowledge = len(load_json(config.SIGNATURE_FILE) or {})
            print(f"║ Blue Signatures  : {blue_knowledge:<3} 📚 {' ' * 38}║")

            red_knowledge = 0
            if 'q1' in red_q: red_knowledge = len(red_q['q1']) + len(red_q['q2'])
            else: red_knowledge = len(red_q)
            print(f"║ Red Knowledge (Q): {red_knowledge:<3} 🧠 {' ' * 38}║")

            # --- RECENT EVENTS ---
            print(f"╠{'═'*60}╣")
            print(f"║ {'AUDIT LOG (Last 5)':^58} ║")
            print(f"╠{'─'*60}╣")

            if os.path.exists(config.AUDIT_LOG):
                try:
                    with open(config.AUDIT_LOG, 'r') as f:
                        lines = f.readlines()
                        for line in lines[-5:]:
                            entry = json.loads(line)
                            actor = entry.get('actor', 'UNKNOWN')
                            action = entry.get('action', 'UNKNOWN')
                            c = "\033[94m" if actor == "BLUE" else "\033[91m"
                            print(f"║ {c}{actor:<4}\033[0m : {action:<15} {' ' * 32}║")
                except: pass

            print(f"╚{'═'*60}╝")
            print("Press Ctrl+C to exit dashboard.")

            time.sleep(2)

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            # print(f"Dashboard Error: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()
