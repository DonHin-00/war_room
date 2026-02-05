#!/usr/bin/env python3
"""
Database Manager
Handles SQLite interactions for high-performance Threat Intel and State management.
"""

import sqlite3
import os
import json
import time
import threading

DB_PATH = "simulation.db"

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Threat Intelligence Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS threat_intel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ioc TEXT UNIQUE NOT NULL,
                    ioc_type TEXT NOT NULL,
                    source TEXT,
                    last_seen REAL,
                    confidence INTEGER DEFAULT 50
                )
            ''')

            # Indexes for speed
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_ioc ON threat_intel(ioc)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON threat_intel(ioc_type)')

            # Simulation State Table (Key-Value)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sim_state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at REAL
                )
            ''')

            # Event Log
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS event_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    team TEXT,
                    action TEXT,
                    details TEXT
                )
            ''')

            conn.commit()
            conn.close()

    # --- THREAT INTEL OPS ---

    def add_iocs(self, iocs, ioc_type="ip", source="unknown"):
        """
        Bulk insert IOCs.
        iocs: list of strings
        """
        if not iocs: return

        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            now = time.time()

            # Prepare data: (ioc, type, source, last_seen)
            data = [(ioc, ioc_type, source, now) for ioc in iocs]

            # UPSERT logic (SQLite 3.24+)
            cursor.executemany('''
                INSERT INTO threat_intel (ioc, ioc_type, source, last_seen)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(ioc) DO UPDATE SET last_seen=excluded.last_seen
            ''', data)

            conn.commit()
            conn.close()

    def get_random_ioc(self, ioc_type="ip"):
        """Get a random IOC of specific type."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT ioc FROM threat_intel WHERE ioc_type=? ORDER BY RANDOM() LIMIT 1', (ioc_type,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else None

    def is_malicious(self, ioc):
        """Check if IOC exists in DB."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM threat_intel WHERE ioc=? LIMIT 1', (ioc,))
        exists = cursor.fetchone() is not None
        conn.close()
        return exists

    def count_iocs(self):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM threat_intel')
        count = cursor.fetchone()[0]
        conn.close()
        return count

    # --- STATE OPS ---

    def get_state(self, key, default=None):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM sim_state WHERE key=?', (key,))
        row = cursor.fetchone()
        conn.close()
        if row:
            try:
                return json.loads(row[0])
            except:
                return row[0]
        return default

    def set_state(self, key, value):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            val_str = json.dumps(value)
            cursor.execute('''
                INSERT INTO sim_state (key, value, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at
            ''', (key, val_str, time.time()))
            conn.commit()
            conn.close()

    # --- LOGGING OPS ---

    def log_event(self, team, action, details):
        with self.lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('INSERT INTO event_log (timestamp, team, action, details) VALUES (?, ?, ?, ?)',
                           (time.time(), team, action, details))
            conn.commit()
            conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.set_state("test", {"a": 1})
    print(db.get_state("test"))
    db.add_iocs(["1.1.1.1", "8.8.8.8"], "ip", "test")
    print(f"Count: {db.count_iocs()}")
