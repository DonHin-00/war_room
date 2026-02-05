#!/usr/bin/env python3
"""
Project: AI Cyber War Simulation (Blue Team)
Repository: https://github.com/DonHin-00/war_room.git
Frameworks: NIST SP 800-61, MITRE Shield
"""

import os
import sys
import time
import random
import logging
import hashlib
from typing import Optional, List, Dict, Any

# Adjust path to import from parent directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import (
    atomic_json_io,
    atomic_json_update,
    atomic_json_merge,
    calculate_file_entropy,
    setup_logging,
    is_honeypot,
    AuditLogger
)
from utils.trace_logger import trace_errors
import config
from ml_engine import DoubleQLearner, SafetyShield

# --- SYSTEM CONFIGURATION ---
setup_logging(config.file_paths['log_file'])
logger = logging.getLogger("BlueBrain")
audit = AuditLogger(config.file_paths['audit_log'])

# --- AI HYPERPARAMETERS ---
ACTIONS: List[str] = config.blue_actions
ALPHA: float = config.hyperparameters['alpha']
ALPHA_DECAY: float = config.hyperparameters['alpha_decay']
GAMMA: float = config.hyperparameters['gamma']
EPSILON: float = config.hyperparameters['epsilon']
EPSILON_DECAY: float = config.hyperparameters['epsilon_decay']
MIN_EPSILON: float = config.hyperparameters['min_epsilon']

# --- VISUALS ---
C_BLUE = "\033[94m"
C_CYAN = "\033[96m"
C_RESET = "\033[0m"

# --- HELPERS ---
def get_file_hash(filepath: str) -> str:
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except:
        return ""

def load_threat_feed() -> List[Dict[str, Any]]:
    try:
        feed = atomic_json_io(config.file_paths['threat_feed'])
        return feed.get('iocs', [])
    except:
        return []

# --- MAIN LOOP ---

@trace_errors
def engage_defense(max_iterations: Optional[int] = None) -> None:

    msg = f"[SYSTEM] Blue Team AI Initialized. Policy: NIST SP 800-61"
    print(f"{C_CYAN}{msg}{C_RESET}")
    logger.info(msg)

    # Initialize ML Engine
    q_table_path = config.file_paths['blue_q_table']
    learner = DoubleQLearner(
        actions=ACTIONS,
        alpha=ALPHA,
        gamma=GAMMA,
        epsilon=EPSILON,
        filepath=q_table_path
    )
    shield = SafetyShield("blue")

    steps_since_save = 0
    save_interval = config.constraints['save_interval']
    watch_dir = config.file_paths['watch_dir']
    network_dir = config.file_paths['network_dir']
    state_file = config.file_paths['state_file']

    known_iocs = load_threat_feed()

    iteration = 0
    try:
        while True:
            if max_iterations is not None and iteration >= max_iterations:
                break
            iteration += 1
            try:
                if iteration % 20 == 0:
                    known_iocs = load_threat_feed()

                # 1. PREPARATION
                war_state: Dict[str, Any] = atomic_json_io(state_file)
                if not war_state: war_state = {'blue_alert_level': 1}

                current_alert = war_state.get('blue_alert_level', 1)
                campaign_phase = war_state.get('red_campaign_phase', 'UNKNOWN')

                # 2. DETECTION
                visible_threats: List[str] = []
                hidden_threats: List[str] = []

                try:
                    with os.scandir(watch_dir) as it:
                        for entry in it:
                            if entry.is_file():
                                if entry.name.startswith('malware_'):
                                    visible_threats.append(entry.path)
                                elif entry.name.startswith('.sys_'):
                                    hidden_threats.append(entry.path)
                except FileNotFoundError:
                    pass

                all_threats = visible_threats + hidden_threats
                threat_count = len(all_threats)

                # Context-Aware State: Alert_Files_Campaign
                state_key = f"{current_alert}_{threat_count}_{campaign_phase}"

                # 3. DECISION
                action = learner.choose_action(state_key)

                # Safety Shield Check
                if shield.is_unsafe(action, {'alert_level': current_alert}):
                    # Override unsafe action
                    action = "OBSERVE"

                # Decay Epsilon
                learner.decay_epsilon(EPSILON_DECAY, MIN_EPSILON)

                # 4. EXECUTION
                mitigated = 0
                trapped = 0
                hunted = 0
                blocked = 0

                if action == "SIGNATURE_SCAN":
                    for t in visible_threats:
                        if not is_honeypot(t):
                            try: os.remove(t); mitigated += 1
                            except: pass

                elif action == "HEURISTIC_SCAN":
                    for t in all_threats:
                        if not is_honeypot(t):
                            if ".sys" in t or calculate_file_entropy(t) > 3.5:
                                try: os.remove(t); mitigated += 1
                                except: pass

                elif action == "THREAT_HUNT":
                    if known_iocs:
                        for t in all_threats:
                            if is_honeypot(t): continue
                            fname = os.path.basename(t)
                            for ioc in known_iocs:
                                if ioc['type'] == 'filename' and ioc['value'] in fname:
                                    try: os.remove(t); hunted += 1
                                    except: pass
                                    break
                                if ioc['type'] == 'hash':
                                    file_hash = get_file_hash(t)
                                    if file_hash == ioc['value']:
                                        try: os.remove(t); hunted += 1
                                        except: pass
                                        break

                elif action == "DEPLOY_DECOY":
                    hp_name = random.choice(config.HONEYPOT_NAMES)
                    hp_path = os.path.join(watch_dir, hp_name)
                    if not os.path.exists(hp_path):
                        try:
                            with open(hp_path, 'w') as f: f.write("SUPER SECRET PASSWORD = admin123")
                            trapped = 1
                            audit.log("BLUE", "HONEYPOT_DEPLOYED", {"file": hp_name})
                        except: pass

                elif action == "DEPLOY_TRAP":
                    # Active Defense: Tar Pits
                    trap_name = "financials.xls"
                    trap_path = os.path.join(watch_dir, trap_name)
                    if not os.path.exists(trap_path):
                        try:
                            with open(trap_path, 'w') as f:
                                f.write("TRAP" * 10000) # Big file to stall read
                            trapped = 1
                            logger.info("🕸️  Blue Team Deployed Tar Pit")
                        except: pass

                elif action == "NETWORK_HUNT":
                    if os.path.exists(network_dir):
                        try:
                            with os.scandir(network_dir) as it:
                                for entry in it:
                                    if entry.is_file() and entry.name.endswith(".pcap"):
                                        try:
                                            os.remove(entry.path)
                                            blocked += 1
                                        except: pass
                        except: pass
                    if blocked > 0:
                        logger.info(f"🚫 Blue Team Blocked {blocked} C2 Packets")

                elif action == "OBSERVE": pass
                elif action == "IGNORE": pass

                # 5. REWARDS
                reward = 0
                if mitigated > 0: reward = config.blue_rewards['mitigation']
                if hunted > 0: reward = config.blue_rewards['threat_hunt_success']
                if trapped > 0: reward = 10
                if blocked > 0: reward = 15

                if campaign_phase == "EXFILTRATION" and action == "NETWORK_HUNT" and blocked > 0:
                    reward += 50
                if campaign_phase == "PERSISTENCE" and action == "HEURISTIC_SCAN" and mitigated > 0:
                    reward += 30

                if action == "HEURISTIC_SCAN" and threat_count == 0: reward = config.blue_rewards['waste']
                if action == "THREAT_HUNT" and hunted == 0: reward = -5
                if action == "NETWORK_HUNT" and blocked == 0 and campaign_phase != "EXFILTRATION": reward = -5

                if current_alert >= 4 and action == "OBSERVE": reward = config.blue_rewards['patience']
                if action == "IGNORE" and threat_count > 0: reward = config.blue_rewards['negligence']

                # 6. LEARN
                # Determine next state
                # Note: This is an approximation since we don't know the exact next state yet
                # We assume the state remains similar for the next Q-Learning step update
                # Or we can just use the same state key since we are in a continuous loop
                # Technically Q-Learning needs Next State.

                # Let's peek at threats again? No that's expensive.
                # We will assume state transitions are somewhat stable or just use the current state
                # as "next state" for the sake of this simplified implementation loop,
                # OR we defer learning until top of loop?
                # Ideally: Store experience in buffer, learn later.
                # For now, let's use the standard loop update with the *same* state as next state approximation
                # or just pass current state_key as both (simplified SARSA-like behavior)

                learner.learn(state_key, action, reward, state_key)

                steps_since_save += 1
                if steps_since_save >= save_interval:
                    learner.save()
                    steps_since_save = 0

                # 7. UPDATE WAR STATE
                should_update = False
                max_alert = config.constraints['max_alert']
                min_alert = config.constraints['min_alert']

                total_success = mitigated + hunted + blocked
                if total_success > 0 and current_alert < max_alert:
                    should_update = True
                elif total_success == 0 and current_alert > min_alert and action == "OBSERVE":
                    should_update = True

                if should_update:
                    def update_state(state):
                        level = state.get('blue_alert_level', 1)
                        if total_success > 0 and level < max_alert:
                            state['blue_alert_level'] = min(max_alert, level + 1)
                        elif total_success == 0 and level > min_alert and action == "OBSERVE":
                            state['blue_alert_level'] = max(min_alert, level - 1)
                        return state
                    atomic_json_update(state_file, update_state)

                if total_success > 0:
                    audit.log("BLUE", "THREAT_MITIGATED", {"action": action, "count": total_success})

                icon = "🛡️ "
                if action == "DEPLOY_TRAP": icon = "🕸️ "
                elif action == "THREAT_HUNT": icon = "🔎"

                # Get max Q for display
                max_q = max([learner.get_q(state_key, a) for a in ACTIONS])

                log_msg = f"{icon} State: {state_key} | Action: {action} | Kill: {total_success} | Q: {max_q:.2f}"
                print(f"{C_BLUE}[BLUE AI]{C_RESET} {log_msg}")
                logger.info(log_msg)

                time.sleep(0.5 if current_alert >= 4 else 1.0)

            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        learner.save()
        logger.info("Blue Team AI Shutting Down")

if __name__ == "__main__":
    engage_defense()
