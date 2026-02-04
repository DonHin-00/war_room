# Centralized Configuration for Red and Blue Teams
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Hyperparameters
# Matching the values from blue_brain.py / red_brain.py
hyperparameters = {
    'alpha': 0.4,             # Learning Rate
    'alpha_decay': 0.9999,
    'gamma': 0.9,             # Discount Factor
    'epsilon': 0.3,           # Exploration Rate
    'epsilon_decay': 0.995,
    'min_epsilon': 0.01,
}

# Rewards (Blue Team)
blue_rewards = {
    'mitigation': 25,
    'patience': 10,
    'waste': -15,
    'negligence': -50,
}

# Rewards (Red Team)
red_rewards = {
    'impact': 10,
    'stealth': 15,
    'critical': 30,
}

# Simulation Constraints
constraints = {
    'max_alert': 5,
    'min_alert': 1,
    'save_interval': 10,
}

# Actions
blue_actions = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE"]
red_actions = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK"]

# File Paths
file_paths = {
    'blue_q_table': os.path.join(BASE_DIR, "blue_q_table.json"),
    'red_q_table': os.path.join(BASE_DIR, "red_q_table.json"),
    'state_file': os.path.join(BASE_DIR, "war_state.json"),
    'watch_dir': "/tmp",
    'log_file': os.path.join(BASE_DIR, "war_room.log"),
    'agents_dir': os.path.join(BASE_DIR, "agents"),
}

# Logging Settings
logging_settings = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
}
