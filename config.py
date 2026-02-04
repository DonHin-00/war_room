# Centralized Configuration for AI Cyber War Simulation

import os

# Base Directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Dynamic Sandbox for Parallel Execution
# Default to 'war_zone' if not specified
WAR_ZONE_ID = os.getenv("WAR_ZONE_ID", "war_zone")
WAR_ZONE_DIR = os.path.join(BASE_DIR, WAR_ZONE_ID)

# File Paths
PATHS = {
    'BLUE_Q_TABLE': os.path.join(WAR_ZONE_DIR, "blue_q_table.json"),
    'RED_Q_TABLE': os.path.join(WAR_ZONE_DIR, "red_q_table.json"),
    'STATE_FILE': os.path.join(WAR_ZONE_DIR, "war_state.json"),
    'WATCH_DIR': WAR_ZONE_DIR,
    'TARGET_DIR': WAR_ZONE_DIR,
    'LOG_FILE': os.path.join(WAR_ZONE_DIR, "war_room.log"),
}

# Blue Team Config
BLUE = {
    'ACTIONS': ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE"],
    'REWARDS': {
        'MITIGATION': 25,
        'PATIENCE': 10,
        'WASTE': -15,
        'NEGLIGENCE': -50,
    },
    'HYPERPARAMETERS': {
        'ALPHA': 0.4,
        'ALPHA_DECAY': 0.9999,
        'GAMMA': 0.9,
        'EPSILON': 0.3,
        'EPSILON_DECAY': 0.995,
        'MIN_EPSILON': 0.01,
        'MEMORY_SIZE': 1000,
        'BATCH_SIZE': 32,
    }
}

# Red Team Config
RED = {
    'ACTIONS': ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK"],
    'REWARDS': {
        'IMPACT': 10,
        'STEALTH': 15,
        'CRITICAL': 30,
    },
    'HYPERPARAMETERS': {
        'ALPHA': 0.4,
        'ALPHA_DECAY': 0.9999,
        'GAMMA': 0.9,
        'EPSILON': 0.3,
        'EPSILON_DECAY': 0.995,
        'MIN_EPSILON': 0.01,
        'MEMORY_SIZE': 1000,
        'BATCH_SIZE': 32,
    }
}

# Simulation Config
SIMULATION = {
    'MAX_ALERT': 5,
    'MIN_ALERT': 1,
}
