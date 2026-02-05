import threading
import time
import os
import sys
import random
from omegabank.app import create_app, db
from omegabank.core.models import User
from irondome.integrity import FileIntegrityMonitor
from irondome.agents import LogAgent
from soc_dashboard import app as soc_app
from sim.clients import run_clients
from sim.adversary import run_adversary

def setup_db(app):
    with app.app_context():
        db.create_all()
        if not User.query.first():
            print("Seeding Database...")
            users = [
                ("admin", "admin123", "admin"),
                ("alice", "password123", "customer"),
                ("bob", "password123", "customer"),
                ("charlie", "password123", "customer"),
                ("dave", "password123", "customer"),
                ("eve", "password123", "customer")
            ]
            for u, p, r in users:
                user = User(username=u, role=r, account_number=f"ACC-{random.randint(1000,9999)}", balance=random.uniform(1000, 50000))
                user.set_password(p)
                db.session.add(user)
            db.session.commit()
            print("Database Seeded.")

def run_bank():
    try:
        app = create_app()
        setup_db(app)
        # Suppress Flask banner
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        app.run(port=5000, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Bank Failed: {e}")

def run_soc():
    try:
        import logging
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR)
        soc_app.run(port=5001, debug=False, use_reloader=False)
    except Exception as e:
        print(f"SOC Failed: {e}")

def run_fim():
    fim = FileIntegrityMonitor("omegabank")
    fim.build_baseline()
    while True:
        time.sleep(10)
        fim.scan()

def run_log_agent():
    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "omegabank", "logs", "app.log")
    agent = LogAgent(log_path)
    agent.run_loop()

if __name__ == "__main__":
    # threads
    threads = []

    t_bank = threading.Thread(target=run_bank, daemon=True)
    threads.append(t_bank)

    t_soc = threading.Thread(target=run_soc, daemon=True)
    threads.append(t_soc)

    t_fim = threading.Thread(target=run_fim, daemon=True)
    threads.append(t_fim)

    t_log = threading.Thread(target=run_log_agent, daemon=True)
    threads.append(t_log)

    print("Starting OmegaBank Ecosystem...")
    for t in threads:
        t.start()

    time.sleep(5)

    # Start Simulators
    t_clients = threading.Thread(target=run_clients, daemon=True)
    t_clients.start()

    t_adv = threading.Thread(target=run_adversary, daemon=True)
    t_adv.start()

    print("Simulation Running. Press Ctrl+C to stop.")
    print("Bank URL: http://localhost:5000")
    print("SOC URL:  http://localhost:5001")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
