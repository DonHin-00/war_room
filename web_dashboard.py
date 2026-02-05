
import flask
import sqlite3
import os
import json
import logging
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Config
DB_PATH = "simulation.db"
LOG_DIR = "logs"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def api_stats():
    data = {
        "alert_level": 1,
        "logs": [],
        "red_q_avg": 0,
        "blue_q_avg": 0
    }

    # 1. Get Alert Level from DB
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM war_state WHERE key='blue_alert_level'")
        row = cursor.fetchone()
        if row:
            data["alert_level"] = int(json.loads(row[0]))

        # 2. Get Q-Table Stats
        cursor.execute("SELECT AVG(value) FROM q_tables WHERE agent='red'")
        row = cursor.fetchone()
        if row and row[0]: data["red_q_avg"] = row[0]

        cursor.execute("SELECT AVG(value) FROM q_tables WHERE agent='blue'")
        row = cursor.fetchone()
        if row and row[0]: data["blue_q_avg"] = row[0]

        conn.close()
    except Exception as e:
        print(f"DB Error: {e}")

    # 3. Get Recent Logs
    # Combine Red, Blue, and Target logs
    logs = []

    def read_tail(filename, label):
        path = os.path.join(LOG_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r') as f:
                # Read last 5 lines efficiently-ish
                lines = f.readlines()[-5:]
                for line in lines:
                    logs.append(f"[{label}] {line.strip()}")

    read_tail("red.log", "RED")
    read_tail("blue.log", "BLUE")
    read_tail("target_http.log", "TARGET")

    # Sort roughly by timestamp (not perfect as format varies, but simple string sort usually puts ISO dates in order)
    # Actually, let's just reverse them so newest are top
    data["logs"] = list(reversed(logs))

    return jsonify(data)

if __name__ == '__main__':
    print("Starting Web Dashboard on 0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080)
