import requests
import random
import time
import logging
import re

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClientSim")

BASE_URL = "http://localhost:5000"
USERNAMES = ["alice", "bob", "charlie", "dave", "eve"]

def get_csrf_token(session, url):
    try:
        response = session.get(url)
        # Simple regex to find the token value
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            return match.group(1)
    except:
        pass
    return None

def simulate_user():
    session = requests.Session()
    username = random.choice(USERNAMES)
    password = "password123"

    # 1. Login
    login_url = f"{BASE_URL}/auth/login"
    token = get_csrf_token(session, login_url)
    if not token: return

    try:
        resp = session.post(login_url, data={
            'username': username,
            'password': password,
            'csrf_token': token
        })
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
            transfer_url = f"{BASE_URL}/banking/transfer"
            token = get_csrf_token(session, transfer_url)
            if token:
                recipient = f"ACC-{random.randint(1000, 9999)}"
                try:
                    session.post(transfer_url, data={
                        'recipient': recipient,
                        'amount': random.uniform(10, 500),
                        'csrf_token': token
                    })
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
