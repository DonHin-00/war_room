#!/usr/bin/env python3
"""
Database Manager
Handles SQLite persistence for the simulation.
"""

import sqlite3
import json
import time
import os
import threading

class DatabaseManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, db_path="simulation.db"):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance.db_path = db_path
                    cls._instance.init_db()
        return cls._instance

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self.get_connection()
        c = conn.cursor()

        # 1. War State Table
        c.execute('''CREATE TABLE IF NOT EXISTS war_state (
                        id INTEGER PRIMARY KEY,
                        key TEXT UNIQUE,
                        value TEXT,
                        updated_at REAL
                    )''')

        # 2. Q-Tables (Red/Blue/Purple)
        c.execute('''CREATE TABLE IF NOT EXISTS q_tables (
                        agent TEXT,
                        state TEXT,
                        action TEXT,
                        value REAL,
                        updated_at REAL,
                        PRIMARY KEY (agent, state, action)
                    )''')

        # 3. Threat Intel (Signatures)
        c.execute('''CREATE TABLE IF NOT EXISTS threat_intel (
                        id INTEGER PRIMARY KEY,
                        type TEXT, -- HASH, IP, DOMAIN
                        value TEXT UNIQUE,
                        confidence REAL,
                        source TEXT,
                        created_at REAL
                    )''')

        # 4. Evolution Log
        c.execute('''CREATE TABLE IF NOT EXISTS evolution_log (
                        id INTEGER PRIMARY KEY,
                        technique TEXT,
                        outcome TEXT, -- SUCCESS, FAIL
                        details TEXT,
                        timestamp REAL
                    )''')

        conn.commit()
        conn.close()

    # --- State Management ---
    def get_state(self, key, default=None):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM war_state WHERE key=?", (key,))
        row = c.fetchone()
        conn.close()
        if row:
            try:
                return json.loads(row[0])
            except:
                return row[0]
        return default

    def set_state(self, key, value):
        conn = self.get_connection()
        c = conn.cursor()
        val_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
        c.execute("INSERT OR REPLACE INTO war_state (key, value, updated_at) VALUES (?, ?, ?)",
                  (key, val_str, time.time()))
        conn.commit()
        conn.close()

    # --- Q-Table Management ---
    def get_q_value(self, agent, state, action, default=0.0):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT value FROM q_tables WHERE agent=? AND state=? AND action=?", (agent, state, action))
        row = c.fetchone()
        conn.close()
        return row[0] if row else default

    def update_q_value(self, agent, state, action, value):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO q_tables (agent, state, action, value, updated_at) VALUES (?, ?, ?, ?, ?)",
                  (agent, state, action, value, time.time()))
        conn.commit()
        conn.close()

    # --- Threat Intel ---
    def add_threat(self, type, value, confidence=1.0, source="simulation"):
        conn = self.get_connection()
        c = conn.cursor()
        try:
            c.execute("INSERT OR IGNORE INTO threat_intel (type, value, confidence, source, created_at) VALUES (?, ?, ?, ?, ?)",
                      (type, value, confidence, source, time.time()))
            conn.commit()
        except: pass
        conn.close()

    def check_threat(self, value):
        conn = self.get_connection()
        c = conn.cursor()
        c.execute("SELECT confidence FROM threat_intel WHERE value=?", (value,))
        row = c.fetchone()
        conn.close()
        return row is not None

if __name__ == "__main__":
    db = DatabaseManager()
    print("Database initialized.")
    db.set_state("test", {"foo": "bar"})
    print(db.get_state("test"))
