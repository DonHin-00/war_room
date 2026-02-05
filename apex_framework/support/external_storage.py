import sqlite3
import json
import os
import time
from typing import Dict, Any, List, Optional

class LongTermDrive:
    """
    External Storage Module.
    Persists War Stories, Blacklists, and IP Reputation.
    """
    def __init__(self, db_path: str = "hive_storage.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS war_stories
                     (id INTEGER PRIMARY KEY, task TEXT, code TEXT, survival_rate REAL)''')
        c.execute('''CREATE TABLE IF NOT EXISTS blacklist
                     (id INTEGER PRIMARY KEY, pattern TEXT, reason TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS ip_reputation
                     (ip TEXT PRIMARY KEY, strikes INTEGER, ban_expiry REAL)''')
        conn.commit()
        conn.close()

    def save_war_story(self, task: str, code: str, survival_rate: float):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO war_stories (task, code, survival_rate) VALUES (?, ?, ?)",
                  (task, code, survival_rate))
        conn.commit()
        conn.close()
        print(f"[STORAGE] 💾 Archived War Story for '{task}' (Survival: {survival_rate:.1%})")

    def get_ip_status(self, ip: str) -> Dict[str, Any]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT strikes, ban_expiry FROM ip_reputation WHERE ip=?", (ip,))
        res = c.fetchone()
        conn.close()
        if res:
            return {"strikes": res[0], "ban_expiry": res[1]}
        return {"strikes": 0, "ban_expiry": 0}

    def add_strike(self, ip: str):
        current = self.get_ip_status(ip)
        strikes = current["strikes"] + 1
        ban_expiry = current["ban_expiry"]

        # Adaptive Banning Logic
        if strikes >= 3:
            # 24 Hour Ban
            ban_expiry = time.time() + 86400
            print(f"[STORAGE] 🚨 IP {ip} has reached 3 strikes. BANNED for 24h.")

        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO ip_reputation (ip, strikes, ban_expiry) VALUES (?, ?, ?)",
                  (ip, strikes, ban_expiry))
        conn.commit()
        conn.close()
