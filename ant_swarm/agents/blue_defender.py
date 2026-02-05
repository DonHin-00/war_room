import os
import glob
import random
import math
import logging
from ant_swarm.core.ooda import OODALoop
from ant_swarm.core.hive import SignalBus

logger = logging.getLogger("BlueDefender")
WATCH_DIR = "/tmp"
Q_TABLE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../", "blue_q_table.json")

class BlueDefender(OODALoop):
    def __init__(self):
        super().__init__("BlueDefender", cycle_time=1.0)
        self.actions = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE", "WIFI_DEFENSE", "WEB_WAF", "NET_IDS"]
        self.q_table = self._load_memory()
        self.alpha = 0.4
        self.epsilon = 0.3

        # Subscribe to relevant events
        self.bus.subscribe("THREAT_DETECTED", self.handle_threat_alert)

    def handle_threat_alert(self, data):
        logger.info(f"Received Threat Alert: {data}")
        # Could trigger immediate reaction

    def observe(self):
        visible_threats = glob.glob(os.path.join(WATCH_DIR, 'malware_*'))
        hidden_threats = glob.glob(os.path.join(WATCH_DIR, '.sys_*'))
        state = self.hive.get_state()
        return {
            "threats": visible_threats + hidden_threats,
            "defcon": state["defcon"],
            "alert_level": state["blue_level"]
        }

    def orient(self, obs):
        threat_count = len(obs["threats"])
        # Classify threats
        web_threats = [t for t in obs["threats"] if t.endswith('.php')]
        wifi_threats = [t for t in obs["threats"] if 'handshake' in t]

        return {
            "state_key": f"{obs['alert_level']}_{threat_count}",
            "threat_count": threat_count,
            "web_threats": web_threats,
            "wifi_threats": wifi_threats,
            "all_threats": obs["threats"]
        }

    def decide(self, orientation):
        state_key = orientation["state_key"]

        # Epsilon-Greedy
        if random.random() < self.epsilon:
            action = random.choice(self.actions)
        else:
            known = {a: self.q_table.get(f"{state_key}_{a}", 0) for a in self.actions}
            action = max(known, key=known.get) if known else random.choice(self.actions)

        return action, orientation

    def act(self, decision_tuple):
        action, orientation = decision_tuple
        mitigated = 0

        if action == "SIGNATURE_SCAN":
            for t in orientation["all_threats"]:
                if not t.endswith('.php'):
                    try: os.remove(t); mitigated += 1
                    except: pass

        elif action == "WEB_WAF":
            for t in orientation["web_threats"]:
                 try: os.remove(t); mitigated += 1
                 except: pass

        elif action == "WIFI_DEFENSE":
            for t in orientation["wifi_threats"]:
                 try: os.remove(t); mitigated += 1
                 except: pass

        elif action == "NET_IDS":
            if orientation["threat_count"] > 0:
                self.hive.update_defcon(max(1, self.hive.get_state()["defcon"] - 1)) # Lower DEFCON = Higher Alert

        elif action == "HEURISTIC_SCAN":
             for t in orientation["all_threats"]:
                if ".sys" in t or self._calculate_entropy(t) > 3.5:
                    try: os.remove(t); mitigated += 1
                    except: pass

        # Reward and Learn (Simplified)
        reward = mitigated * 10
        if action == "IGNORE" and orientation["threat_count"] > 0: reward -= 10

        self._learn(orientation["state_key"], action, reward)

        # Publish update
        if mitigated > 0:
            self.bus.publish("THREAT_MITIGATED", {"count": mitigated, "action": action})
            logger.info(f"Action: {action} | Mitigated: {mitigated}")

    def _learn(self, state, action, reward):
        old = self.q_table.get(f"{state}_{action}", 0)
        self.q_table[f"{state}_{action}"] = old + self.alpha * (reward - old)

        # Periodic Save
        if random.random() < 0.1:
            self._save_memory()

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

    def _calculate_entropy(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                if not data: return 0
                entropy = 0
                for x in range(256):
                    p_x = float(data.count(x.to_bytes(1, 'little'))) / len(data)
                    if p_x > 0:
                        entropy += - p_x * math.log(p_x, 2)
                return entropy
        except: return 0
