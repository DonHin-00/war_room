#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Red Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: MITRE ATT&CK Matrix
"""

import os
import sys
import time
import random
import logging
from typing import Optional, List, Dict, Any

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    atomic_json_io,
    atomic_json_update,
    atomic_json_merge,
    setup_logging,
    is_honeypot,
    AuditLogger,
    is_tar_pit
)
from utils.trace_logger import trace_errors
import config
from ml_engine import DoubleQLearner, SafetyShield

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("RedBrain")
audit = AuditLogger(config.file_paths['audit_log'])

# --- AI HYPERPARAMETERS ---
ACTIONS: List[str] = config.red_actions
ALPHA: float = config.hyperparameters['alpha']
ALPHA_DECAY: float = config.hyperparameters['alpha_decay']
GAMMA: float = config.hyperparameters['gamma']
EPSILON: float = config.hyperparameters['epsilon']
EPSILON_DECAY: float = config.hyperparameters['epsilon_decay']
MIN_EPSILON: float = config.hyperparameters['min_epsilon']

# --- VISUALS ---
C_RED = "\033[91m"
C_RESET = "\033[0m"

# --- CAMPAIGN MANAGER ---
class RedCampaignManager:
    """
    Manages the Cyber Kill Chain state.
    Phases: RECON -> WEAPONIZE -> DELIVERY -> EXPLOIT -> INSTALL -> C2 -> ACTIONS
    Simplified for this sim: RECON -> OBFUSCATE (Delivery) -> ROOTKIT (Exploit) -> PERSISTENCE -> EXFIL
    """
    def __init__(self):
        self.chain = [
            "T1046_RECON",
            "T1027_OBFUSCATE",
            "T1003_ROOTKIT",
            "T1547_PERSISTENCE",
            "T1041_EXFILTRATION"
        ]
        self.current_index = 0

    def get_current_objective(self) -> str:
        return self.chain[self.current_index]

    def advance(self):
        if self.current_index < len(self.chain) - 1:
            self.current_index += 1

    def reset(self):
        self.current_index = 0

    def get_phase_name(self) -> str:
        return self.chain[self.current_index].split('_')[1]

# --- MAIN LOOP ---

@trace_errors
def engage_offense(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Red Team AI Initialized. APT Framework: ACTIVE"
    print(f"{C_RED}{msg}{C_RESET}")
    logger.info(msg)

    q_table_path = config.file_paths['red_q_table']

    # Initialize ML Engine
    learner = DoubleQLearner(
        actions=ACTIONS,
        alpha=ALPHA,
        gamma=GAMMA,
        epsilon=EPSILON,
        filepath=q_table_path
    )
    shield = SafetyShield("red")

    steps_since_save = 0
    save_interval = config.constraints['save_interval']
    target_dir = config.file_paths['watch_dir']
    state_file = config.file_paths['state_file']
    persist_dir = config.file_paths['persistence_dir']
    exfil_dir = config.file_paths['exfil_dir']

    campaign = RedCampaignManager()

    # Ensure attack dirs exist
    for d in [persist_dir, exfil_dir]:
        if not os.path.exists(d):
            try: os.makedirs(d)
            except: pass

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1
            try:
                # 1. RECON & STATE AWARENESS
                war_state: Dict[str, Any] = atomic_json_io(state_file)
                if not war_state: war_state = {'blue_alert_level': 1}

                current_alert = war_state.get('blue_alert_level', 1)

                # Update State with Campaign Phase for Dashboard
                war_state['red_campaign_phase'] = campaign.get_phase_name()
                war_state['red_campaign_index'] = campaign.current_index
                war_state['red_campaign_total'] = len(campaign.chain)

                state_key = f"{current_alert}_{campaign.get_phase_name()}"

                # LOW AND SLOW
                if current_alert >= 4:
                    time.sleep(random.uniform(2.0, 5.0))

                # 2. STRATEGY SELECTION
                action: str = ""

                # Force Campaign Progression if low alert, otherwise rely on Learner
                # We blend campaign logic with Epsilon-Greedy from ML Engine

                if random.random() < learner.epsilon:
                     if random.random() < 0.5:
                        action = campaign.get_current_objective()
                     else:
                        action = random.choice(ACTIONS)
                else:
                    action = learner.choose_action(state_key)

                learner.decay_epsilon(EPSILON_DECAY, MIN_EPSILON)

                # 3. EXECUTION
                impact = 0
                burned = False
                success = False

                if action == "T1046_RECON":
                    try:
                        with os.scandir(target_dir) as it:
                            for entry in it:
                                if is_honeypot(entry.path):
                                    burned = True
                                    audit.log("RED", "TRIPPED_HONEYPOT", {"file": entry.name})
                                    break
                                if is_tar_pit(entry.path):
                                    time.sleep(2.0)
                                    break
                    except: pass

                    if not burned:
                        fname = os.path.join(target_dir, f"malware_bait_{int(time.time())}.sh")
                        try:
                            with open(fname, 'w') as f: f.write("echo 'scan'")
                            impact = 1
                            success = True
                        except: pass

                elif action == "T1027_OBFUSCATE":
                    fname = os.path.join(target_dir, f"malware_crypt_{int(time.time())}.bin")
                    try:
                        payload = os.urandom(1024)
                        padding = os.urandom(random.randint(100, 500))
                        with open(fname, 'wb') as f: f.write(payload + padding)
                        impact = 3
                        success = True
                    except: pass

                elif action == "T1003_ROOTKIT":
                    fname = os.path.join(target_dir, f".sys_shadow_{int(time.time())}")
                    try:
                        with open(fname, 'w') as f: f.write("uid=0(root)")
                        impact = 5
                        success = True
                    except: pass

                elif action == "T1589_LURK":
                    impact = 0
                    success = True

                elif action == "T1547_PERSISTENCE":
                    p_name = os.path.join(persist_dir, "update_service.sh")
                    try:
                        with open(p_name, 'w') as f:
                            f.write("#!/bin/bash\n# Re-spawn malware\ntouch /tmp/battlefield/malware_respawned.bin")
                        impact = 5
                        success = True
                        logger.info(f"⚓ Red Team Established Persistence: {p_name}")
                        audit.log("RED", "PERSISTENCE_CREATED", {"file": p_name})
                    except: pass

                elif action == "T1041_EXFILTRATION":
                    s_name = os.path.join(exfil_dir, f"data_{int(time.time())}.zip")
                    try:
                        with open(s_name, 'wb') as f:
                            f.write(os.urandom(2048))
                        time.sleep(0.5)
                        os.remove(s_name)
                        impact = 6
                        success = True
                        logger.info("📤 Red Team Exfiltrated Data")
                        audit.log("RED", "DATA_EXFILTRATION", {"size": 2048})
                    except: pass

                # Campaign Logic
                if burned:
                    campaign.reset()
                elif success and action == campaign.get_current_objective():
                    campaign.advance()

                if action == "T1041_EXFILTRATION" and success:
                    campaign.reset()
                    logger.info("🏆 Red Team Completed Kill Chain!")

                # 4. REWARDS
                reward = 0
                max_alert = config.constraints['max_alert']
                if impact > 0: reward = config.red_rewards['impact']
                if current_alert >= 4 and action == "T1589_LURK": reward = config.red_rewards['stealth']
                if current_alert == max_alert and impact > 0: reward = config.red_rewards['critical']
                if action == "T1547_PERSISTENCE" and impact > 0: reward = config.red_rewards['persistence']
                if action == "T1041_EXFILTRATION" and impact > 0: reward = config.red_rewards['exfil']
                if burned: reward = config.red_rewards['burned']

                if success and action == campaign.get_current_objective():
                    reward += 5

                # 5. LEARN
                learner.learn(state_key, action, reward, state_key)

                steps_since_save += 1
                if steps_since_save >= save_interval:
                    learner.save()
                    steps_since_save = 0

                # 6. TRIGGER ALERTS & UPDATE STATE
                if impact > 0 or burned:
                    def update_state(state):
                        if impact > 0 and random.random() > 0.5:
                            state['blue_alert_level'] = min(max_alert, state.get('blue_alert_level', 1) + 1)
                        # Always update campaign status
                        state['red_campaign_phase'] = campaign.get_phase_name()
                        state['red_campaign_index'] = campaign.current_index
                        return state

                    atomic_json_update(state_file, update_state)

                if impact > 0:
                    max_q = max([learner.get_q(state_key, a) for a in ACTIONS])
                    log_msg = f"👹 State: {state_key} | Tech: {action} | Impact: {impact} | Burned: {burned} | Q: {max_q:.2f}"
                    print(f"{C_RED}[RED AI] {C_RESET} {log_msg}")
                    logger.info(log_msg)

                time.sleep(random.uniform(0.5, 1.5))

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        learner.save()
        logger.info("Red Team AI Shutting Down")

if __name__ == "__main__":
    engage_offense()
