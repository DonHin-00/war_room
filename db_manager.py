
import sqlite3
import os
import json
import logging
import time

class DatabaseManager:
    def __init__(self, db_path="simulation.db"):
        self.db_path = db_path
        self.conn = None
        # self._init_db() # Lazy initialization

    def _ensure_connection(self):
        """Ensure DB is connected."""
        if self.conn is None:
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

    def _execute_with_retry(self, query, params=(), commit=False):
        """Execute a query with retry logic for locking errors."""
        self._ensure_connection()
        for i in range(5):
            try:
                self.cursor.execute(query, params)
                if commit:
                    self.conn.commit()
                return self.cursor
            except sqlite3.OperationalError as e:
                if "locked" in str(e):
                    time.sleep(0.1 * (i + 1))
                else:
                    raise e
            except Exception as e:
                logging.error(f"DB Error: {e}")
                break
        return None

    # --- State Management ---
    def get_state(self, key, default=None):
        try:
            cursor = self._execute_with_retry("SELECT value FROM war_state WHERE key = ?", (key,))
            if cursor:
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
            return default
        except Exception as e:
            logging.error(f"DB Read Error: {e}")
            return default

    def set_state(self, key, value):
        self._execute_with_retry(
            "INSERT OR REPLACE INTO war_state (key, value) VALUES (?, ?)",
            (key, json.dumps(value)),
            commit=True
        )

    # --- Q-Learning ---
    def get_q_value(self, agent, state, action):
        cursor = self._execute_with_retry(
            "SELECT value FROM q_tables WHERE agent=? AND state=? AND action=?",
            (agent, state, action)
        )
        if cursor:
            row = cursor.fetchone()
            return row[0] if row else 0.0
        return 0.0

    def update_q_value(self, agent, state, action, value):
        self._execute_with_retry(
            "INSERT OR REPLACE INTO q_tables (agent, state, action, value) VALUES (?, ?, ?, ?)",
            (agent, state, action, value),
            commit=True
        )

    def get_best_action(self, agent, state, actions):
        # Optimization: Let SQL do the sorting
        placeholders = ','.join('?' for _ in actions)
        query = f'''
            SELECT action, value FROM q_tables
            WHERE agent=? AND state=? AND action IN ({placeholders})
            ORDER BY value DESC LIMIT 1
        '''
        params = [agent, state] + actions

        cursor = self._execute_with_retry(query, params)
        if cursor:
            row = cursor.fetchone()
            if row:
                return row[0]
        return None

    # --- Threat Intel ---
    def add_threat(self, type_, value, source="simulation"):
        self._execute_with_retry(
            "INSERT OR IGNORE INTO threat_intel (type, value, source, added_at) VALUES (?, ?, ?, ?)",
            (type_, value, source, time.time()),
            commit=True
        )

    def is_threat(self, type_, value):
        cursor = self._execute_with_retry(
            "SELECT 1 FROM threat_intel WHERE type=? AND value=?",
            (type_, value)
        )
        return cursor.fetchone() is not None if cursor else False

    def get_random_threat_filename(self):
        cursor = self._execute_with_retry(
            "SELECT value FROM threat_intel WHERE type='filename' ORDER BY RANDOM() LIMIT 1"
        )
        if cursor:
            row = cursor.fetchone()
            return row[0] if row else None
        return None

    # --- Experience Replay ---
    def save_experience(self, agent, state, action, reward, next_state, source='real'):
        self._execute_with_retry('''
            INSERT INTO experience_replay (agent, state, action, reward, next_state, timestamp, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (agent, state, action, reward, next_state, time.time(), source), commit=True)

    def sample_experience(self, agent, batch_size=10):
        cursor = self._execute_with_retry('''
            SELECT state, action, reward, next_state FROM experience_replay
            WHERE agent=? ORDER BY RANDOM() LIMIT ?
        ''', (agent, batch_size))
        return cursor.fetchall() if cursor else []

    def close(self):
        self.conn.close()
