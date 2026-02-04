import sqlite3
import json
import os
from typing import Dict, Any, List

class LongTermDrive:
    """
    External Storage Module.
    Persists War Stories and Blacklists to SQLite.
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
        conn.commit()
        conn.close()

    def save_war_story(self, task: str, code: str, survival_rate: float):
        """Stores a successful code generation."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO war_stories (task, code, survival_rate) VALUES (?, ?, ?)",
                  (task, code, survival_rate))
        conn.commit()
        conn.close()
        print(f"[STORAGE] 💾 Archived War Story for '{task}' (Survival: {survival_rate:.1%})")

    def add_blacklist_pattern(self, pattern: str, reason: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO blacklist (pattern, reason) VALUES (?, ?)", (pattern, reason))
        conn.commit()
        conn.close()

    def get_blacklist(self) -> List[tuple]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT pattern, reason FROM blacklist")
        data = c.fetchall()
        conn.close()
        return data
