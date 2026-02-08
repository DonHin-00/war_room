from flask import Flask, render_template, jsonify
import json
import os
import time

app = Flask(__name__, template_folder='irondome/templates', static_folder='irondome/static')
SIEM_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "irondome/logs/siem.json")

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def stats():
    events = []
    if os.path.exists(SIEM_LOG_FILE):
        try:
            with open(SIEM_LOG_FILE, 'r') as f:
                for line in f:
                    try: events.append(json.loads(line))
                    except: pass
        except: pass

    # Process stats
    total_events = len(events)
    critical = len([e for e in events if e.get('severity') == 'CRITICAL'])
    warning = len([e for e in events if e.get('severity') == 'WARNING'])

    # Recent logs
    recent = sorted(events, key=lambda x: x['timestamp'], reverse=True)[:15]

    return jsonify({
        'total': total_events,
        'critical': critical,
        'warning': warning,
        'recent': recent
    })

if __name__ == "__main__":
    app.run(port=5001, debug=True)
