#!/usr/bin/env python3
import socket
import struct
import time
import json
import threading
import sys
import os
import random
import uuid

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
import utils

# Configuration
SWARM_GRP = '224.2.2.2'
SWARM_PORT = 5008
AGENT_ID = str(uuid.uuid4())[:8]

logger = utils.setup_logging(f"BlueSwarm-{AGENT_ID}", config.BLUE_LOG)

class BlueSwarmAgent:
    def __init__(self):
        self.immunity_db = set()
        self.running = True

    def setup_multicast(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', SWARM_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(SWARM_GRP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def share_intel(self, ioc):
        """Gossip Protocol: Share IOC with Swarm."""
        if ioc in self.immunity_db: return

        msg = {
            "sender": AGENT_ID,
            "type": "IOC_Found",
            "ioc": ioc,
            "ts": time.time()
        }
        data = json.dumps(msg).encode('utf-8')
        try:
            self.sender.sendto(data, (SWARM_GRP, SWARM_PORT))
            logger.info(f"Broadcasted IOC: {ioc}")
        except Exception: pass

    def listener(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = json.loads(data.decode('utf-8'))

                if msg.get('sender') == AGENT_ID: continue

                if msg.get('type') == "IOC_Found":
                    ioc = msg.get('ioc')
                    if ioc not in self.immunity_db:
                        self.immunity_db.add(ioc)
                        logger.info(f"Received Shared Immunity: {ioc}")

            except Exception: pass

    def hunt(self):
        # Simulated Hunting Loop
        while self.running:
            # Simulate finding a threat periodically
            if random.random() > 0.8:
                fake_hash = utils.calculate_checksum(f"malware_{random.randint(1,1000)}")
                if fake_hash not in self.immunity_db:
                    self.immunity_db.add(fake_hash)
                    logger.info(f"Detected Threat: {fake_hash}")
                    self.share_intel(fake_hash)
            time.sleep(2)

    def run(self):
        logger.info(f"Blue Swarm Agent {AGENT_ID} activated.")
        utils.enforce_seccomp() # Hardening
        self.setup_multicast()

        t = threading.Thread(target=self.listener)
        t.daemon = True
        t.start()

        self.hunt()

if __name__ == "__main__":
    agent = BlueSwarmAgent()
    try:
        agent.run()
    except KeyboardInterrupt:
        pass
