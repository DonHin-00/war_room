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
        self.q_table = {}
        self.epsilon = 0.3
        self.alpha = 0.4

    def choose_strategy(self):
        """Select action based on Q-Learning."""
        actions = ["POLYMORPH", "STEGO", "FLOOD_C2", "FUZZ_BLUE"]
        state = "DEFAULT" # Simplified state

        if random.random() < self.epsilon:
            return random.choice(actions)
        else:
            return max(actions, key=lambda a: self.q_table.get(f"{state}_{a}", 0))

    def learn(self, action, reward):
        """Update Q-Table."""
        state = "DEFAULT"
        old_val = self.q_table.get(f"{state}_{action}", 0)
        self.q_table[f"{state}_{action}"] = old_val + self.alpha * (reward - old_val)

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
            "genes": self.genes, # Share genes for Crossover
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

    def listener(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(1024)
                msg = json.loads(data.decode('utf-8'))

                sender = msg.get('sender')
                if sender == NODE_ID: continue # Ignore self

                # Gene Harvesting
                if 'genes' in msg:
                    self.peer_genes[sender] = msg['genes']

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

    def establish_persistence(self):
        """Simulate dropping persistence artifacts."""
        if random.random() < 0.3: # 30% chance
            svc_name = f"systemd-worker-{secrets.token_hex(4)}.service"
            target = os.path.join(config.PERSISTENCE_DIR, svc_name)
            content = f"[Unit]\nDescription=Worker {NODE_ID}\n[Service]\nExecStart=/usr/bin/python3 red_node.py"

            # We don't have a token here easily in this architecture,
            # or we assume Red nodes bypass auth or steal tokens.
            # For sim, we try to create it.
            if not os.path.exists(target):
                try:
                    with open(target, 'w') as f: f.write(content)
                    logger.info(f"Persistence established: {svc_name}")
                except Exception: pass

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
