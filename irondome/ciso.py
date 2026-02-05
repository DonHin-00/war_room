import time
import os
from agents.blue_agent import BlueAgent
from omegabank.core.system_state import system_state
from irondome.siem import SIEM_LOG_FILE

class CISO_AI:
    def __init__(self):
        self.agent = BlueAgent()
        self.last_state = "DEFCON_1"
        self.log_file = SIEM_LOG_FILE

    def _analyze_siem(self):
        # Count recent critical alerts
        critical_count = 0
        try:
            if os.path.exists(self.log_file):
                # Tail last 20 lines
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()[-20:]
                    for line in lines:
                        if "CRITICAL" in line: critical_count += 1
        except: pass
        return critical_count

    def run_loop(self):
        print("Starting AI CISO...")
        while True:
            # 1. Observe
            threat_level = system_state.get_threat_level() # 0-100
            critical_alerts = self._analyze_siem()

            # Construct State String
            if critical_alerts > 5 or threat_level > 50:
                current_state = "HIGH_THREAT"
            elif critical_alerts > 0:
                current_state = "MODERATE_THREAT"
            else:
                current_state = "LOW_THREAT"

            # 2. Decide
            action = self.agent.get_action(current_state)
            system_state.ai_blue_action = action

            # 3. Act (Update Policy)
            if action == "DEFCON_5":
                system_state.defcon = 5
                system_state.rate_limit_multiplier = 0.1 # Very Strict
            elif action == "DEFCON_3":
                system_state.defcon = 3
                system_state.rate_limit_multiplier = 0.5
            elif action == "DEFCON_1":
                system_state.defcon = 1
                system_state.rate_limit_multiplier = 1.0
            elif action == "RESET_FILTERS":
                # Maybe clear blocklists (simulated)
                pass

            # 4. Reward
            # If threat level goes down, reward +
            reward = 0
            if current_state == "LOW_THREAT" and action == "DEFCON_1": reward = 10 # Good efficiency
            if current_state == "HIGH_THREAT" and action == "DEFCON_5": reward = 20 # Good response
            if current_state == "LOW_THREAT" and action == "DEFCON_5": reward = -10 # Overreaction

            # 5. Learn
            # We assume next state is whatever happens after sleep
            self.agent.learn(self.last_state, action, reward, current_state)
            self.last_state = current_state

            time.sleep(2)

def run_ciso():
    ciso = CISO_AI()
    ciso.run_loop()
