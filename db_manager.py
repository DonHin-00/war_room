
import sqlite3
import os
import json
import logging
import time

class DatabaseManager:
    def __init__(self, db_path="simulation.db"):
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()

        # Enable WAL mode for concurrency (Retry if locked)
        for _ in range(5):
            try:
                self.conn.execute("PRAGMA journal_mode=WAL;")
                break
            except sqlite3.OperationalError:
                time.sleep(0.2)

        # 1. War State Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS war_state (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')

        # 2. Q-Tables (Shared schema for agents)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS q_tables (
                agent TEXT,
                state TEXT,
                action TEXT,
                value REAL,
                PRIMARY KEY (agent, state, action)
            )
        ''')

        # 3. Threat Intelligence
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS threat_intel (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT, -- 'hash' or 'filename'
                value TEXT UNIQUE,
                source TEXT,
                added_at REAL
            )
        ''')

        # 4. Experience Replay (Reinforced Info + Shadow Learning)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS experience_replay (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent TEXT,
                state TEXT,
                action TEXT,
                reward REAL,
                next_state TEXT,
                timestamp REAL,
                source TEXT DEFAULT 'real' -- 'real' or 'proxy'
            )
        ''')

        self.conn.commit()

    # --- State Management ---
    def get_state(self, key, default=None):
        try:
            self.cursor.execute("SELECT value FROM war_state WHERE key = ?", (key,))
            row = self.cursor.fetchone()
            if row:
                return json.loads(row[0])
            return default
        except Exception as e:
            logging.error(f"DB Read Error: {e}")
            return default

    def set_state(self, key, value):
        try:
            self.cursor.execute("INSERT OR REPLACE INTO war_state (key, value) VALUES (?, ?)",
                               (key, json.dumps(value)))
            self.conn.commit()
        except Exception as e:
            logging.error(f"DB Write Error: {e}")

    # --- Q-Learning ---
    def get_q_value(self, agent, state, action):
        self.cursor.execute("SELECT value FROM q_tables WHERE agent=? AND state=? AND action=?",
                           (agent, state, action))
        row = self.cursor.fetchone()
        return row[0] if row else 0.0

    def update_q_value(self, agent, state, action, value):
        self.cursor.execute("INSERT OR REPLACE INTO q_tables (agent, state, action, value) VALUES (?, ?, ?, ?)",
                           (agent, state, action, value))
        self.conn.commit()

    def get_best_action(self, agent, state, actions):
        # Optimization: Let SQL do the sorting
        placeholders = ','.join('?' for _ in actions)
        query = f'''
            SELECT action, value FROM q_tables
            WHERE agent=? AND state=? AND action IN ({placeholders})
            ORDER BY value DESC LIMIT 1
        '''
        params = [agent, state] + actions
        self.cursor.execute(query, params)
        row = self.cursor.fetchone()

        # If we have a known best, return it
        if row:
            return row[0]
        # Otherwise random (caller handles exploration, but here we return None or let caller decide)
        return None

    # --- Threat Intel ---
    def add_threat(self, type_, value, source="simulation"):
        try:
            self.cursor.execute("INSERT OR IGNORE INTO threat_intel (type, value, source, added_at) VALUES (?, ?, ?, ?)",
                               (type_, value, source, time.time()))
            self.conn.commit()
        except: pass

    def is_threat(self, type_, value):
        self.cursor.execute("SELECT 1 FROM threat_intel WHERE type=? AND value=?", (type_, value))
        return self.cursor.fetchone() is not None

    def get_random_threat_filename(self):
        self.cursor.execute("SELECT value FROM threat_intel WHERE type='filename' ORDER BY RANDOM() LIMIT 1")
        row = self.cursor.fetchone()
        return row[0] if row else None

    # --- Experience Replay ---
    def save_experience(self, agent, state, action, reward, next_state, source='real'):
        self.cursor.execute('''
            INSERT INTO experience_replay (agent, state, action, reward, next_state, timestamp, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (agent, state, action, reward, next_state, time.time(), source))
        # Keep buffer size manageable (e.g., last 1000)
        # Note: Doing this every insert is slow, maybe optimize later or use a scheduled job
        # For now, just let it grow, simulation is short.
        self.conn.commit()

    def sample_experience(self, agent, batch_size=10):
        self.cursor.execute('''
            SELECT state, action, reward, next_state FROM experience_replay
            WHERE agent=? ORDER BY RANDOM() LIMIT ?
        ''', (agent, batch_size))
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()
