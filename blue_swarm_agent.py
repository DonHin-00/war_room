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
import signal
import urllib.parse
import math
import collections
from vnet.nic import VNic
from vnet.protocol import MSG_DATA

# Configuration
SWARM_GRP = '224.2.2.2'
SWARM_PORT = 5008
AGENT_ID = str(uuid.uuid4())[:8]

logger = utils.setup_logging(f"BlueSwarm-{AGENT_ID}", config.BLUE_LOG)

class EDRMonitor:
    """Host-Based EDR Capability."""
    def scan_network(self):
        """Scan /proc/net/tcp for unauthorized listeners."""
        threats = []
        try:
            with open("/proc/net/tcp", "r") as f:
                next(f)
                for line in f:
                    parts = line.strip().split()
                    if not parts: continue
                    if parts[3] == "0A": # LISTEN
                        ip, port_hex = parts[1].split(':')
                        port = int(port_hex, 16)
                        # Detect Red Mesh Port
                        if port == 5007:
                            threats.append(parts[9]) # inode
        except Exception: pass
        return threats

    def scan_processes(self):
        """Scan process list for Red signatures."""
        threat_pids = []
        for pid in os.listdir("/proc"):
            if not pid.isdigit(): continue
            try:
                with open(f"/proc/{pid}/cmdline", 'rb') as f:
                    cmd = f.read().replace(b'\0', b' ')
                    if b"red_mesh_node" in cmd or b"red_node" in cmd:
                        threat_pids.append(int(pid))
            except Exception: pass
        return threat_pids

    def terminate(self, pid):
        try:
            os.kill(pid, signal.SIGKILL)
            return True
        except Exception: return False

class SoarEngine:
    """Decentralized SOAR Capability."""
    def __init__(self, token, nic):
        self.lockdown_active = False
        self.token = token
        self.nic = nic
        self.blocked_ips = set()

    def evaluate(self, threat_level):
        """Trigger playbooks based on threat level."""
        if threat_level > 5 and not self.lockdown_active:
            self.activate_lockdown()
        elif threat_level < 2 and self.lockdown_active:
            self.deactivate_lockdown()

    def block_ip(self, ip):
        if ip in self.blocked_ips: return

        logger.warning(f"SOAR: 🚫 BLOCKING IP {ip}")
        # Send CONTROL message to Switch
        # Type 'CONTROL' is not in MSG_DATA enum usually, but protocol handles strings.
        # We need to ensure we use the right type.

        payload = {"cmd": "BLOCK", "target": ip}
        self.nic.send("switch", payload, msg_type="CONTROL")
        self.blocked_ips.add(ip)

    def activate_lockdown(self):
        self.lockdown_active = True
        logger.warning("SOAR: 🔒 ACTIVATING ISOLATION PROTOCOL")
        # Sim: Change dir permissions or block comms
        # We simulate by creating a lock file that prevents Red from dropping payloads
        try:
            lock_file = os.path.join(config.SIMULATION_DATA_DIR, ".lockdown")
            utils.secure_create(lock_file, "LOCKED", token=self.token)
        except Exception: pass

    def deactivate_lockdown(self):
        self.lockdown_active = False
        logger.info("SOAR: 🔓 DEACTIVATING ISOLATION PROTOCOL")
        try:
            lock_file = os.path.join(config.SIMULATION_DATA_DIR, ".lockdown")
            if os.path.exists(lock_file): os.remove(lock_file)
        except Exception: pass

class BlueSwarmAgent:
    def __init__(self):
        self.immunity_db = set()
        self.trust_db = {} # {agent_id: score}
        self.running = True

        # Auth
        self.id_mgr = utils.IdentityManager(config.SESSION_DB)
        self.token = self.id_mgr.login(f"BlueSwarm-{AGENT_ID}")

        # Virtual Network
        self.nic = VNic(f"10.0.1.{random.randint(2,254)}", is_tap=(random.random() < 0.2))
        self.network_threats_detected = 0

        self.edr = EDRMonitor()
        self.soar = SoarEngine(self.token, self.nic)

        # RL Defense
        self.brain = utils.RLBrain(f"BlueSwarm-{AGENT_ID}",
                                   ["TIGHTEN_TRUST", "LOOSEN_TRUST", "SOAR_LOCKDOWN", "HUNT_AGGRESSIVE"])
        self.anomaly_engine = utils.AnomalyDetector()

        # Insider Threat Logic
        self.is_rogue = random.random() < 0.1 # 10% chance
        if self.is_rogue:
            logger.warning("⚠️  INSIDER THREAT: This agent has been compromised (ROGUE)")

        # Deception (Honeypots)
        self.honeypots = {} # path -> last_mtime
        self.deploy_honeypots()

    def deploy_honeypots(self):
        """Deploy decoy files to catch Red Team."""
        for name in config.HONEYPOT_NAMES:
            path = os.path.join(config.SIMULATION_DATA_DIR, name)
            if not os.path.exists(path):
                try:
                    with open(path, 'w') as f:
                        f.write(f"CONFIDENTIAL DATA for {name}\n")
                        f.write(f"Generated by Agent {AGENT_ID}\n")
                    logger.info(f"Deployed Honeypot: {name}")
                except: pass

            # Record state for monitoring
            if os.path.exists(path):
                self.honeypots[path] = os.path.getmtime(path)

    def check_honeypots(self):
        """Monitor honeypots for access/modification."""
        for path, last_mtime in self.honeypots.items():
            if not os.path.exists(path):
                logger.critical(f"HONEYPOT ALERT: {os.path.basename(path)} was DELETED!")
                self.share_intel(f"HONEYPOT_TRIGGER_{os.path.basename(path)}")
                # Re-deploy
                self.deploy_honeypots()
                continue

            try:
                curr_mtime = os.path.getmtime(path)
                # Check for modification
                if curr_mtime != last_mtime:
                    logger.critical(f"HONEYPOT ALERT: {os.path.basename(path)} was ACCESSED/MODIFIED!")
                    self.share_intel(f"HONEYPOT_TRIGGER_{os.path.basename(path)}")
                    self.honeypots[path] = curr_mtime
            except: pass

    def setup_multicast(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(('', SWARM_PORT))

        # Fix: Use 4s4s for 64-bit compatibility (Group, Interface)
        mreq = struct.pack("4s4s", socket.inet_aton(SWARM_GRP), socket.inet_aton("0.0.0.0"))
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

        self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    def start_network_ops(self):
        """Connect to VNet and start operations."""
        if self.nic.connect():
            role = "IDS Monitor (TAP)" if self.nic.is_tap else "Endpoint"
            logger.info(f"Connected to VNet as {self.nic.ip} [{role}]")
            t = threading.Thread(target=self.network_listener, daemon=True)
            t.start()
        else:
            logger.warning("VNet connection failed.")

    def calculate_entropy(self, data):
        if not data: return 0
        counts = collections.Counter(data)
        entropy = 0
        length = len(data)
        for count in counts.values():
            p = count / length
            entropy -= p * math.log2(p)
        return entropy

    def network_listener(self):
        """Monitor network traffic for signatures (IDS)."""
        last_check = time.time()
        packet_count = 0

        while self.running and self.nic.connected:
            msg = self.nic.recv(timeout=0.1)

            # Anomaly Detection: Volume
            now = time.time()
            packet_count += 1
            if now - last_check > 1.0:
                if packet_count > 50: # Threshold
                    logger.warning(f"IDS ALERT: Volumetric Anomaly ({packet_count} pps)")
                packet_count = 0
                last_check = now

            if msg and self.nic.is_tap:
                # IDS Analysis
                raw_payload = str(msg.get('payload', ''))
                src = msg.get('src')

                # 1. Entropy Check (Encrypted C2 Detection)
                entropy = self.calculate_entropy(raw_payload)
                if entropy > 4.5 and len(raw_payload) > 50:
                    logger.warning(f"IDS ALERT: High Entropy ({entropy:.2f}) from {src} - Possible Encrypted C2")
                    # No automatic ban, just alert

                # 2. Normalization
                decoded_payload = urllib.parse.unquote(raw_payload)

                # 3. Signatures (on both raw and decoded)
                signatures = ["OR '1'='1", "<script>", "1=1", "alert("]

                threat = False
                for sig in signatures:
                    if sig in raw_payload or sig in decoded_payload:
                        threat = True
                        break

                # 4. Hex Decode Check
                if "\\x" in raw_payload:
                    try:
                        # Simple check if lots of hex
                        if raw_payload.count("\\x") > 5: threat = True
                    except: pass

                if threat:
                    logger.critical(f"IDS ALERT: Attack detected from {src}")
                    self.network_threats_detected += 1
                    self.share_intel(f"NET_ATTACK_{src}")

                    # Active Response (Block IP)
                    self.soar.block_ip(src)

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
            # 0. EDR: Process & Network Hunt
            red_pids = self.edr.scan_processes()
            for pid in red_pids:
                if self.edr.terminate(pid):
                    logger.critical(f"EDR: Terminated Red Node PID {pid}")
                    self.share_intel(f"PROCESS_KILL_{pid}")

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

            # Anomaly Detection Input
            # Simulating file ops metric
            file_ops = len(os.listdir(config.SIMULATION_DATA_DIR))
            self.anomaly_engine.add_datapoint(file_ops)
            is_anomaly = self.anomaly_engine.is_anomaly(file_ops)

            # RL Defense Decision
            threat_level = len(self.immunity_db)
            state = "ANOMALY" if is_anomaly else ("HIGH_THREAT" if threat_level > 5 else "LOW_THREAT")

            action = self.brain.choose_action(state)

            reward = 0
            if action == "TIGHTEN_TRUST":
                reward = 2 if is_anomaly else -1
            elif action == "SOAR_LOCKDOWN":
                if is_anomaly or threat_level > 10:
                    self.soar.evaluate(threat_level + 10)
                    reward = 10
                else:
                    reward = -5 # False Positive
            elif action == "HUNT_AGGRESSIVE":
                self.edr.scan_processes()
                reward = 5 if is_anomaly else 1
            elif action == "LOOSEN_TRUST":
                reward = 1 if not is_anomaly else -10

            # Learn
            self.brain.learn(state, action, reward, state)
            self.brain.save()

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
        self.start_network_ops()

        # Auto-Healing Listener
        while self.running:
            t = threading.Thread(target=self.listener)
            t.daemon = True
            t.start()

            try:
                self.check_honeypots() # Check traps
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
