# Centralized Configuration for Red and Blue Teams
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File Paths
PATHS = {
    'BASE_DIR': BASE_DIR,
    'BLUE_Q_TABLE': os.path.join(BASE_DIR, "blue_q_table.json"),
    'RED_Q_TABLE': os.path.join(BASE_DIR, "red_q_table.json"),
    'STATE_FILE': os.path.join(BASE_DIR, "war_state.json"),
    'BATTLEFIELD': os.path.join(BASE_DIR, "battlefield"),
    'SESSIONS_DIR': os.path.join(BASE_DIR, "sessions"),
    'SIGNATURE_DB': os.path.join(BASE_DIR, "signatures.json"),
    'EVOLUTION_LOG': os.path.join(BASE_DIR, "evolution.json"),
    'AUDIT_LOG': os.path.join(BASE_DIR, "audit.jsonl"),
    'BACKUPS': os.path.join(BASE_DIR, "backups"),
}

# Ensure directories exist
for path in [PATHS['BATTLEFIELD'], PATHS['SESSIONS_DIR'], PATHS['BACKUPS']]:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# Hyperparameters (Shared defaults, can be overridden per agent if needed)
HYPERPARAMETERS = {
    'ALPHA': 0.4,             # Learning Rate
    'ALPHA_DECAY': 0.9999,    # Stability Factor
    'GAMMA': 0.9,             # Discount Factor
    'EPSILON': 0.3,           # Exploration Rate
    'EPSILON_DECAY': 0.995,   # Mastery Curve
    'MIN_EPSILON': 0.01,
}

# Blue Team Configuration
BLUE = {
    'ACTIONS': ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE", "BACKUP_CRITICAL"],
    'REWARDS': {
        'MITIGATION': 25,
        'PATIENCE': 10,
        'WASTE': -15,
        'NEGLIGENCE': -50,
    },
    'ALERTS': {
        'MAX': 5,
        'MIN': 1,
    }
}

# Red Team Configuration
RED = {
    'ACTIONS': ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK", "T1486_ENCRYPT", "T1071_WEB_TRAFFIC"],
    'REWARDS': {
        'IMPACT': 10,
        'STEALTH': 15,
        'CRITICAL': 30,
    },
    'ALERTS': {
        'MAX': 5,
    }
}

# Logging Settings
LOGGING = {
    'level': 'DEBUG',
    'format': '%(asctime)s %(levelname)s:%(message)s',
    'file': os.path.join(BASE_DIR, 'simulation.log')
}
