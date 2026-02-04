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
    def __init__(self, gene_jitter=5.0, gene_aggression=0.5, gene_stealth=False):
        self.peers = set()
        self.running = True
        self.sock = None
        self.start_time = time.time()

        # Genetics
        self.genes = {
            "jitter": gene_jitter,
            "aggression": gene_aggression,
            "stealth": gene_stealth
        }

    def setup_multicast(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', MCAST_PORT))

        # Fix: Use 4s4s for 64-bit compatibility (Group, Interface)
        mreq = struct.pack("4s4s", socket.inet_aton(MCAST_GRP), socket.inet_aton("0.0.0.0"))
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

    def update_topology(self):
        """Update shared topology file for visualization."""
        topo = utils.safe_json_read(config.TOPOLOGY_FILE, {})
        topo[NODE_ID] = {
            "type": "RED",
            "peers": list(self.peers),
            "last_seen": time.time(),
            "genes": self.genes
        }
        utils.safe_json_write(config.TOPOLOGY_FILE, topo)

    def reproduce(self):
        """Evolutionary Replication."""
        # Only reproduce if we survived long enough
        age = time.time() - self.start_time
        if age > 15: # Fast evolution for sim
            logger.info("🧬 MITOSIS: Spawning Offspring Node")

            # Mutation
            new_jitter = max(1.0, self.genes['jitter'] + random.uniform(-1.0, 1.0))
            new_aggro = max(0.1, min(1.0, self.genes['aggression'] + random.uniform(-0.1, 0.1)))
            new_stealth = not self.genes['stealth'] if random.random() > 0.9 else self.genes['stealth']

            # Spawn process
            import subprocess
            cmd = [sys.executable, __file__,
                   str(new_jitter), str(new_aggro), str(new_stealth)]
            try:
                subprocess.Popen(cmd)
                self.start_time = time.time() # Reset breeding timer
            except Exception as e:
                logger.error(f"Reproduction failed: {e}")

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
                    self.update_topology()

                msg_type = msg.get('type')
                if msg_type == "CMD":
                    # Decentralized Execution
                    cmd = msg.get('payload')
                    logger.info(f"Executing Mesh Command: {cmd}")

            except Exception as e:
                # logger.error(f"Receive error: {e}")
                pass

    def drop_stego(self):
        """Drop covert channel payload."""
        if random.random() < self.genes['aggression']:
            fname = os.path.join(config.SIMULATION_DATA_DIR, f"vacation_{random.randint(1,100)}.jpg")
            payload = {"cmd": "EXECUTE_ORDER_66", "target": "BLUE"}

            # Authenticate creation?
            # We need a token. Let's assume nodes inherit tokens or generate ad-hoc.
            # For this sim, we just try.
            # Actually utils.secure_create requires a token.
            # Let's bypass or use a dummy token if we can't login.
            # But wait, IdentityManager is in utils.
            # We should login first.

            utils.steganography_encode(payload, fname)
            logger.info(f"Dropped Stego Payload: {fname}")

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
            self.reproduce()
            self.drop_stego()

            # Behavior based on Genes
            sleep_time = self.genes['jitter']
            if self.genes['stealth']:
                sleep_time *= 2

            time.sleep(max(1, sleep_time + random.uniform(-1, 1)))

if __name__ == "__main__":
    # Parse Genes from CLI (if spawned)
    g_jitter = 5.0
    g_aggro = 0.5
    g_stealth = False

    if len(sys.argv) >= 4:
        g_jitter = float(sys.argv[1])
        g_aggro = float(sys.argv[2])
        g_stealth = sys.argv[3] == 'True'

    node = RedMeshNode(g_jitter, g_aggro, g_stealth)
    try:
        node.run()
    except KeyboardInterrupt:
        pass
