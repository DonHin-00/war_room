
import utils
import emulator
import random
import os

class ProxyRed:
    def __init__(self, sandbox):
        self.sandbox = sandbox
        # Load real threats
        self.threat_loader = utils.SmartJSONLoader("threat_db.json", {'filenames': []})

    def act(self):
        # 1. Pick a Persona/Sample
        # SmartJSONLoader.load returns (data, changed) tuple
        res = self.threat_loader.load()
        if isinstance(res, tuple):
            db = res[0]
        else:
            db = res

        names = db.get('filenames', [])
        sample_name = random.choice(names) if names else "generic_malware.exe"
        sample_name = os.path.basename(sample_name)

        # 2. Spawn in Sandbox
        pid = self.sandbox.spawn_process(sample_name)

        # 3. Emulate Behavior
        # Simple heuristic mapping based on name
        behavior = "LURK"
        if "crypt" in sample_name or "lock" in sample_name:
            self.sandbox.emul_ransomware(pid)
            behavior = "RANSOMWARE"
        elif "bot" in sample_name or "agent" in sample_name:
            self.sandbox.emul_c2_beacon(pid, "192.168.1.100")
            behavior = "C2"
        else:
            # Default to cleanup/evasion
            self.sandbox.emul_cleanup(pid)
            behavior = "EVASION"

        return pid, sample_name, behavior

class ProxyBlue:
    def __init__(self, sandbox):
        self.sandbox = sandbox
        # Read-Only access to Main Blue Brain's wisdom
        self.q_manager = utils.QTableManager("blue", ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "IGNORE"])

    def react(self, pid, sample_name, behavior):
        # 1. Observe Sandbox Event
        # For proxy war, we simplify state to "DETECTED_{BEHAVIOR}"
        state_key = f"PROXY_{behavior}"

        # 2. Consult Main Brain (Transfer Learning)
        # If Main Brain has seen this, use its wisdom. Else, try Heuristic.
        action = self.q_manager.get_best_action(state_key)
        if not action:
            action = "HEURISTIC_SCAN"

        # 3. Execute in Sandbox
        reward = 0
        if action == "SIGNATURE_SCAN":
            # Simulate hash check success
            self.sandbox.kill_process(pid)
            reward = 10
        elif action == "HEURISTIC_SCAN":
            # Behavior check
            if behavior in ["RANSOMWARE", "C2"]:
                self.sandbox.kill_process(pid)
                reward = 15
            else:
                reward = -5 # False positive risk or waste
        elif action == "IGNORE":
            if behavior == "LURK":
                reward = 5
            else:
                reward = -20

        # 4. Report to Experience Replay (Shadow Learning)
        # Next state is effectively "RESOLVED" or "COMPROMISED"
        next_state = "RESOLVED" if reward > 0 else "COMPROMISED"
        utils.DB.save_experience("blue", state_key, action, reward, next_state, source='proxy')

        return action, reward
