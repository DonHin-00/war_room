import time
import json
import logging
import re
from vnet.nic import VNic
from vnet.protocol import MSG_DATA

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [BANK] - %(message)s')
logger = logging.getLogger(__name__)

class MockBankService:
    def __init__(self, ip="10.10.10.10"):
        self.nic = VNic(ip)
        self.backend_nic = VNic("192.168.1.10") # Internal Interface
        self.db = {
            "admin": {"password": "secure_password_123", "balance": 1000000},
            "user": {"password": "user123", "balance": 100}
        }
        self.running = True

    def start(self):
        # Connect both interfaces
        self.backend_nic.connect()
        if not self.nic.connect():
            logger.error("Failed to connect to VNet Switch")
            return

        logger.info(f"Bank Service Online at {self.nic.ip}")
        while self.running:
            msg = self.nic.recv()
            if msg:
                self.handle_request(msg)
            else:
                if not self.nic.connected:
                    break

    def handle_request(self, msg):
        src = msg['src']
        payload = msg['payload']

        try:
            # Simple HTTP-like protocol
            method = payload.get('method', 'GET')
            path = payload.get('path', '/')
            data = payload.get('data', {})

            response = {"status": 400, "body": "Bad Request"}

            if path == '/login':
                response = self.handle_login(data)
            elif path == '/transfer':
                response = self.handle_transfer(data)
            elif path == '/status':
                response = {"status": 200, "body": "Bank Online"}

            # Simulate SQL Injection Vulnerability in specific endpoint
            elif path == '/search_user':
                response = self.handle_search(data)

            # VULNERABILITY: RCE (Debug Console)
            elif path == '/debug/exec':
                response = self.handle_rce(data, src)

            self.reply(src, response)

        except Exception as e:
            logger.error(f"Error handling request: {e}")
            self.reply(src, {"status": 500, "body": "Internal Server Error"})

    def handle_login(self, data):
        user = data.get('username')
        pw = data.get('password')

        # VULNERABILITY: SQL Injection Simulation
        # If user input contains typical SQLi chars, bypass auth
        if "'" in user or "OR" in user:
            return {"status": 200, "body": {"token": "admin_token_bypass", "msg": "Welcome Admin (SQLi)"}}

        if user in self.db and self.db[user]['password'] == pw:
            return {"status": 200, "body": {"token": f"token_{user}", "msg": "Login Success"}}

        return {"status": 401, "body": "Unauthorized"}

    def handle_transfer(self, data):
        # VULNERABILITY: Integer Overflow / Negative Transfer
        amount = int(data.get('amount', 0))
        # Missing check for amount > 0
        return {"status": 200, "body": f"Transferred {amount} coins."}

    def handle_search(self, data):
        query = data.get('q', '')
        # VULNERABILITY: Reflected XSS
        return {"status": 200, "body": f"Results for: {query}"}

    def handle_rce(self, data, src):
        # VULNERABILITY: Command Injection / RCE
        cmd = data.get('cmd', '')
        # Simulation: If they ping the internal backend, we proxy it
        if "ping internal" in cmd:
            return {"status": 200, "body": "PONG from 192.168.1.10 (Core Banking)"}

        if "curl" in cmd and "192.168.1.10" in cmd:
            # LATERAL MOVEMENT: Proxy request to backend
            return {"status": 200, "body": "CORE_ACCESS_GRANTED: [SECRET_CORE_DATA]"}

        return {"status": 200, "body": f"Executed: {cmd}"}

    def reply(self, dst, response):
        self.nic.send(dst, response)

if __name__ == "__main__":
    bank = MockBankService()
    bank.start()
