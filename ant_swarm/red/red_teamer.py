import os
import time
import random
import logging
from ant_swarm.core.ooda import OODALoop

logger = logging.getLogger("RedTeamer")
TARGET_DIR = "/tmp"

class RedTeamer(OODALoop):
    def __init__(self):
        super().__init__("RedTeamer", cycle_time=1.5)
        self.actions = [
            "T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK",
            "T1046_WIFI_SCAN", "T1046_NET_SCAN", "T1190_WEB_EXPLOIT"
        ]
        self.q_table = {}
        self.epsilon = 0.3
        self.alpha = 0.4

    def observe(self):
        # Red team observes the defensive posture (via Hive or direct recon)
        # For simulation, it just acts based on its own state/randomness mostly
        return self.hive.get_state()

    def orient(self, obs):
        return {"defcon": obs["defcon"]}

    def decide(self, orientation):
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            # Simple choice logic
            action = random.choice(self.actions)
        return action

    def act(self, action):
        impact = 0
        fname = None

        if action == "T1046_RECON":
            fname = f"malware_bait_{int(time.time())}.sh"
            content = "echo 'scan'"
            impact = 1

        elif action == "T1027_OBFUSCATE":
            fname = f"malware_crypt_{int(time.time())}.bin"
            content = os.urandom(1024)
            impact = 3

        elif action == "T1003_ROOTKIT":
            fname = f".sys_shadow_{int(time.time())}"
            content = "uid=0(root)"
            impact = 5

        elif action == "T1190_WEB_EXPLOIT":
            fname = f"malware_webshell_{int(time.time())}.php"
            content = "<?php system($_GET['cmd']); ?>"
            impact = 7

        elif action == "T1046_WIFI_SCAN":
             # Drop handshake file
             fname = f"handshake_{int(time.time())}.cap"
             content = b"handshake_data"
             impact = 2

        if fname:
            try:
                path = os.path.join(TARGET_DIR, fname)
                mode = 'wb' if isinstance(content, bytes) else 'w'
                with open(path, mode) as f: f.write(content)
                logger.info(f"Executed {action}: Dropped {fname}")
                self.bus.publish("ATTACK_LAUNCHED", {"action": action, "impact": impact})
            except Exception as e:
                logger.error(f"Failed to execute {action}: {e}")

        # Reduce epsilon
        self.epsilon *= 0.995
