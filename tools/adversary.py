#!/usr/bin/env python3
import sys
import os
import time
import threading
import random
import socket
import struct
import json
import logging

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vnet.protocol import MSG_HELLO, MSG_DATA, pack_message
from vnet.nic import VNic

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ADVERSARY] - %(message)s')
logger = logging.getLogger(__name__)

SWITCH_HOST = '127.0.0.1'
SWITCH_PORT = 10000

class Adversary:
    def __init__(self):
        self.nics = []

    def attack_connection_flood(self, count=50):
        """DoS: Exhaust switch connection limits."""
        logger.info(f"⚔️  ATTACK: Connection Flood ({count} connections)...")
        for i in range(count):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((SWITCH_HOST, SWITCH_PORT))
                # Don't handshake, just hold
                self.nics.append(sock)
            except Exception as e:
                logger.error(f"Flood failed at {i}: {e}")
                break
        time.sleep(2)
        logger.info("Releasing flood connections...")
        for s in self.nics:
            s.close()
        self.nics = []

    def attack_packet_flood(self):
        """DoS: Flood switch with valid packets."""
        logger.info("⚔️  ATTACK: Packet Flood...")
        nic = VNic("10.6.6.6")
        if not nic.connect():
            logger.error("Could not connect for packet flood")
            return

        for i in range(1000):
            nic.send("broadcast", {"spam": "A"*100})
            if i % 100 == 0: time.sleep(0.01)
        nic.close()

    def attack_malformed_protocol(self):
        """Fuzz: Send garbage data to switch."""
        logger.info("⚔️  ATTACK: Protocol Fuzzing...")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((SWITCH_HOST, SWITCH_PORT))

            # 1. Bad Length
            sock.sendall(b'\xFF\xFF\xFF\xFF' + b'JUNK')

            # 2. Bad JSON
            msg = b'{"type": "HELLO", "src": "BAD", ' # Incomplete
            sock.sendall(struct.pack('!I', len(msg)) + msg)

            sock.close()
        except Exception as e:
            logger.error(f"Fuzzing error: {e}")

    def attack_obfuscation(self):
        """Evasion: Send encoded payloads to bypass IDS."""
        logger.info("⚔️  ATTACK: Obfuscation Evasion...")
        nic = VNic("10.6.6.7")
        if not nic.connect(): return

        target = "10.10.10.10" # Bank

        # Send obvious attack FIRST to trigger block
        logger.info("Sending obvious attack to trigger SOAR...")
        nic.send(target, {"method": "POST", "path": "/login", "data": {"username": "admin' OR '1'='1"}})
        time.sleep(2) # Wait for block

        # Try sending again - should fail (or be dropped)
        logger.info("Sending second attack (should be blocked)...")
        nic.send(target, {"method": "POST", "path": "/login", "data": {"username": "admin"}})

        nic.close()

    def run_all(self):
        logger.info("Starting Adversarial Test Suite")

        self.attack_obfuscation()
        time.sleep(2)

        self.attack_malformed_protocol()
        time.sleep(2)

        self.attack_packet_flood()
        time.sleep(2)

        self.attack_connection_flood()

        logger.info("Adversarial Tests Complete.")

if __name__ == "__main__":
    adv = Adversary()
    adv.run_all()
