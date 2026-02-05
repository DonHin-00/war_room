import requests
import random
import time
import logging

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClientSim")

BASE_URL = "http://localhost:5000"
USERNAMES = ["alice", "bob", "charlie", "dave", "eve"]

def simulate_user():
    session = requests.Session()
    username = random.choice(USERNAMES)
    password = "password123"

    # 1. Login
    try:
        resp = session.post(f"{BASE_URL}/auth/login", data={'username': username, 'password': password})
        if resp.status_code != 200:
            return
    except:
        return

    # 2. Activity
    actions = ["check_balance", "transfer", "logout"]
    for _ in range(random.randint(1, 5)):
        action = random.choice(actions)
        if action == "check_balance":
            try: session.get(f"{BASE_URL}/banking/dashboard")
            except: pass
        elif action == "transfer":
            recipient = f"ACC-{random.randint(1000, 9999)}"
            try: session.post(f"{BASE_URL}/banking/transfer", data={'recipient': recipient, 'amount': random.uniform(10, 500)})
            except: pass

        time.sleep(random.uniform(0.5, 2))

    try: session.get(f"{BASE_URL}/auth/logout")
    except: pass

def run_clients():
    print("Starting Client Simulation...")
    while True:
        simulate_user()
        time.sleep(random.uniform(1, 3))

if __name__ == "__main__":
    run_clients()
