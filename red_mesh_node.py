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
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
NODE_ID = str(uuid.uuid4())[:8]

logger = utils.setup_logging(f"RedNode-{NODE_ID}", config.RED_LOG)

class RedMeshNode:
    def __init__(self):
        self.peers = set()
        self.running = True
        self.sock = None

    def setup_multicast(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MCAST_PORT))

        mreq = struct.pack("4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        # Sender socket
        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def broadcast(self, msg_type, payload):
        """Send message to mesh."""
        msg = {
            "ver": 1,
            "sender": NODE_ID,
            "type": msg_type,
            "payload": payload,
            "ts": time.time()
        }
        data = json.dumps(msg).encode('utf-8')
        try:
            self.sender.sendto(data, (MCAST_GRP, MCAST_PORT))
        except Exception as e:
            logger.error(f"Broadcast failed: {e}")

    def listener(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = json.loads(data.decode('utf-8'))

                sender = msg.get('sender')
                if sender == NODE_ID: continue # Ignore self

                if sender not in self.peers:
                    self.peers.add(sender)
                    logger.info(f"New Peer Discovered: {sender}")

                msg_type = msg.get('type')
                if msg_type == "CMD":
                    # Decentralized Execution
                    cmd = msg.get('payload')
                    logger.info(f"Executing Mesh Command: {cmd}")

            except Exception as e:
                # logger.error(f"Receive error: {e}")
                pass

    def run(self):
        logger.info(f"Red Mesh Node {NODE_ID} coming online...")
        utils.enforce_seccomp() # Hardening
        self.setup_multicast()

        t = threading.Thread(target=self.listener)
        t.daemon = True
        t.start()

        # Heartbeat / Beacon
        while self.running:
            self.broadcast("HEARTBEAT", "Still Alive")
            time.sleep(random.randint(3, 8))

if __name__ == "__main__":
    node = RedMeshNode()
    try:
        node.run()
    except KeyboardInterrupt:
        pass
