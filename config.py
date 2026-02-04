# Centralized Configuration for Red and Blue Teams
import os

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Simulation Directories
SIMULATION_DATA_DIR = os.path.join(BASE_DIR, "simulation_data")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
NETWORK_BUS_DIR = os.path.join(BASE_DIR, "network_bus")
MODELS_DIR = os.path.join(BASE_DIR, "models")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# State Files
Q_TABLE_BLUE = os.path.join(BASE_DIR, "blue_q_table.json")
Q_TABLE_RED = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
SIGNATURE_DB = os.path.join(BASE_DIR, "signatures.json")
SESSION_DB = os.path.join(BASE_DIR, "sessions.json")

# Hyperparameters
HYPERPARAMETERS = {
    'learning_rate': 0.4,
    'learning_rate_decay': 0.9999,
    'discount_factor': 0.9,
    'epsilon': 0.3,
    'epsilon_decay': 0.995,
    'min_epsilon': 0.01
}

# Blue Team Config
BLUE_ACTIONS = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "DEPLOY_DECEPTION", "BACKUP_CRITICAL", "NETWORK_FILTER", "OBSERVE", "IGNORE"]
BLUE_REWARDS = {
    'mitigation': 25,
    'recovery': 50,
    'patience': 10,
    'waste': -15,
    'negligence': -50,
    'trap_success': 100
}

# Deception
HONEYPOT_NAMES = ["admin_creds.db", "prod_config.xml", "wallet.dat", "vpn_keys.pem"]

# Defcon Levels (SOAR)
DEFCON_LEVELS = {
    5: "NORMAL",
    4: "ELEVATED",
    3: "HIGH_ALERT",
    2: "LOCKDOWN",
    1: "NUCLEAR_OPTION"
}

# Red Team Config
RED_ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1486_ENCRYPT", "T1071_WEB_TRAFFIC", "T1589_LURK"]
RED_REWARDS = {
    'impact': 10,
    'stealth': 15,
    'ransom': 40,
    'critical': 30,
    'burned': -100
}

# Alert Levels
MIN_ALERT = 1
MAX_ALERT = 5

# Resource Limits
MAX_DIR_SIZE_MB = 100  # 100MB limit for simulation data
MAX_MEMORY_MB = 50     # 50MB RAM limit per agent
MAX_CPU_PERCENT = 80   # Not easily enforceable via resource module, but noted.

# Ensure directories exist
for d in [SIMULATION_DATA_DIR, BACKUP_DIR, NETWORK_BUS_DIR, MODELS_DIR, LOGS_DIR]:
    if not os.path.exists(d):
        try:
            os.makedirs(d, mode=0o700)
        except OSError:
            pass

# Log Files
BLUE_LOG = os.path.join(LOGS_DIR, "blue.log")
RED_LOG = os.path.join(LOGS_DIR, "red.log")
AUDIT_LOG = os.path.join(LOGS_DIR, "audit.jsonl")
