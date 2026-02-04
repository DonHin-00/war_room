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
        self.trust_db = {} # {agent_id: score}
        self.running = True

        # Insider Threat Logic
        self.is_rogue = random.random() < 0.1 # 10% chance
        if self.is_rogue:
            logger.warning("⚠️  INSIDER THREAT: This agent has been compromised (ROGUE)")

    def setup_multicast(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', SWARM_PORT))

        # Fix: Use 4s4s for 64-bit compatibility (Group, Interface)
        mreq = struct.pack("4s4s", socket.inet_aton(SWARM_GRP), socket.inet_aton("0.0.0.0"))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def share_intel(self, ioc):
        """Gossip Protocol: Share IOC with Swarm."""
        if ioc in self.immunity_db: return

        payload_ioc = ioc

        # ROGUE AGENT: Poison the well
        if self.is_rogue and random.random() > 0.5:
            # Broadcast a FALSE FLAG (whitelist a known bad, or blacklist a good)
            # Here we just broadcast junk to spam
            payload_ioc = "FALSE_FLAG_" + uuid.uuid4().hex
            logger.info(f"😈 ROGUE ACTION: Broadcasting False Flag {payload_ioc}")

        msg = {
            "sender": AGENT_ID,
            "type": "IOC_Found",
            "ioc": payload_ioc,
            "ts": time.time()
        }
        data = json.dumps(msg).encode('utf-8')
        try:
            self.sender.sendto(data, (SWARM_GRP, SWARM_PORT))
            if not self.is_rogue:
                logger.info(f"Broadcasted IOC: {ioc}")
        except Exception: pass

    def update_topology(self):
        """Update shared topology file for visualization."""
        topo = utils.safe_json_read(config.TOPOLOGY_FILE, {})
        topo[AGENT_ID] = {
            "type": "BLUE",
            "peers": ["SWARM"], # Abstract peer for Swarm
            "last_seen": time.time()
        }
        utils.safe_json_write(config.TOPOLOGY_FILE, topo)

    def listener(self):
        self.update_topology()
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = json.loads(data.decode('utf-8'))

                # Replay Protection
                msg_ts = msg.get('ts', 0)
                if time.time() - msg_ts > 5.0:
                    # logger.warning("Dropping Replay/Old Message")
                    continue

                sender = msg.get('sender')
                if sender == AGENT_ID: continue

                # Trust Logic
                current_trust = self.trust_db.get(sender, 50) # Neutral start

                if msg.get('type') == "IOC_Found":
                    ioc = msg.get('ioc')

                    # Rogue Detection: If IOC looks like obvious junk (e.g. "FALSE_FLAG"), penalize
                    if "FALSE_FLAG" in ioc:
                        self.trust_db[sender] = max(0, current_trust - 20)
                        logger.warning(f"Trust Drop for {sender}: {self.trust_db[sender]} (Bad Intel)")
                        continue

                    # Consensus: Only accept if trusted OR we verified it
                    if current_trust > 30:
                        if ioc not in self.immunity_db:
                            self.immunity_db.add(ioc)
                            logger.info(f"Received Shared Immunity: {ioc} (Trust: {current_trust})")
                    else:
                        logger.debug(f"Ignoring IOC from untrusted {sender}")

                elif msg.get('type') == "VOUCH":
                    # Peer verification increases trust
                    target_agent = msg.get('target')
                    if target_agent in self.trust_db:
                        self.trust_db[target_agent] = min(100, self.trust_db[target_agent] + 5)
                        logger.info(f"Trust Boost for {target_agent}: {self.trust_db[target_agent]}")

            except Exception: pass

    def hunt(self):
        # Simulated Hunting Loop
        while self.running:
            # 1. Scan for Steganography
            import glob
            images = glob.glob(os.path.join(config.SIMULATION_DATA_DIR, "*.jpg"))
            for img in images:
                hidden = utils.steganography_decode(img)
                if hidden:
                    logger.warning(f"STEGANOGRAPHY DETECTED in {img}: {hidden}")
                    try:
                        os.remove(img)
                        logger.info(f"Neutralized Covert Channel: {img}")
                    except Exception: pass

            # 2. Simulate finding a threat periodically
            if random.random() > 0.8:
                fake_hash = utils.calculate_checksum(f"malware_{random.randint(1,1000)}")
                if fake_hash not in self.immunity_db:
                    self.immunity_db.add(fake_hash)
                    logger.info(f"Detected Threat: {fake_hash}")
                    self.share_intel(fake_hash)

            # 3. Hunt Persistence
            persistence = glob.glob(os.path.join(config.PERSISTENCE_DIR, "*.service"))
            for p in persistence:
                logger.critical(f"PERSISTENCE FOUND: {os.path.basename(p)}")
                try:
                    os.remove(p)
                    logger.info("Persistence mechanism purged.")
                except Exception: pass

            # Verify/Vouch logic (Simulation)
            # If this hash matches something recently shared by a peer, VOUCH for them
            # (Simplified: Random vouching for simulation aliveness)
            if self.trust_db and random.random() > 0.7:
                peer = random.choice(list(self.trust_db.keys()))
                self.broadcast_vouch(peer)

            time.sleep(2)

    def broadcast_vouch(self, target_agent):
        """Broadcast trust vote."""
        msg = {
            "sender": AGENT_ID,
            "type": "VOUCH",
            "target": target_agent,
            "ts": time.time()
        }
        data = json.dumps(msg).encode('utf-8')
        try:
            self.sender.sendto(data, (SWARM_GRP, SWARM_PORT))
        except Exception: pass

    def run(self):
        logger.info(f"Blue Swarm Agent {AGENT_ID} activated.")
        utils.enforce_seccomp() # Hardening
        self.setup_multicast()

        # Auto-Healing Listener
        while self.running:
            t = threading.Thread(target=self.listener)
            t.daemon = True
            t.start()

            try:
                self.hunt() # Main loop
            except Exception as e:
                logger.error(f"Agent Crash: {e}. Auto-Healing...")
                time.sleep(1)

if __name__ == "__main__":
    agent = BlueSwarmAgent()
    try:
        agent.run()
    except KeyboardInterrupt:
        pass
