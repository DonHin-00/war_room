import os

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WAR_ZONE_DIR = os.path.join(BASE_DIR, "battlefield")
DATA_DIR = os.path.join(BASE_DIR, "simulation_data")
INCIDENT_DIR = os.path.join(DATA_DIR, "incidents")

# Ensure directories exist
os.makedirs(WAR_ZONE_DIR, exist_ok=True, mode=0o700)
os.makedirs(DATA_DIR, exist_ok=True, mode=0o700)
os.makedirs(INCIDENT_DIR, exist_ok=True, mode=0o700)

PATHS = {
    "BASE_DIR": BASE_DIR,
    "WAR_ZONE": WAR_ZONE_DIR,
    "Q_TABLE_RED": os.path.join(DATA_DIR, "red_q_table.json"),
    "Q_TABLE_BLUE": os.path.join(DATA_DIR, "blue_q_table.json"),
    "WAR_STATE": os.path.join(DATA_DIR, "war_state.json"),
    "SIGNATURES": os.path.join(DATA_DIR, "signatures.json"),
    "AUDIT_LOG": os.path.join(DATA_DIR, "audit.jsonl"),
    "INCIDENTS": INCIDENT_DIR,
    "LOG_RED": os.path.join(BASE_DIR, "red.log"),
    "LOG_BLUE": os.path.join(BASE_DIR, "blue.log"),
    "LOG_MAIN": os.path.join(BASE_DIR, "war_room.log"),
}

# --- HYPERPARAMETERS ---
RL = {
    "ALPHA": 0.4,
    "ALPHA_DECAY": 0.9999,
    "GAMMA": 0.9,
    "EPSILON_START": 0.3,
    "EPSILON_MIN": 0.01,
    "EPSILON_DECAY": 0.995,
    "BATCH_SIZE": 8,
    "MEMORY_CAPACITY": 1000,
    "SYNC_INTERVAL": 10
}

# --- RED TEAM CONFIG ---
RED = {
    "ACTIONS": [
        "T1046_RECON",
        "T1027_OBFUSCATE",
        "T1003_ROOTKIT",
        "T1589_LURK",
        "T1036_MASQUERADE",
        "T1486_ENCRYPT",    # Ransomware
        "T1071_C2_BEACON"   # C2 Communication
    ],
    "REWARDS": {
        "IMPACT": 10,
        "STEALTH": 15,
        "CRITICAL": 30,
        "PENALTY_TRAPPED": -20
    }
}

# --- BLUE TEAM CONFIG ---
BLUE = {
    "ACTIONS": [
        "SIGNATURE_SCAN",
        "HEURISTIC_SCAN",
        "OBSERVE",
        "IGNORE",
        "DEPLOY_TRAP",
        "DEPLOY_DECOY",
        "BACKUP_CRITICAL",  # Backup data
        "RESTORE_DATA"      # Restore from backup
    ],
    "REWARDS": {
        "MITIGATION": 25,
        "PATIENCE": 10,
        "TRAP_SUCCESS": 50,
        "PENALTY_WASTE": -15,
        "PENALTY_NEGLIGENCE": -50,
        "ANOMALY_BONUS": 20,
        "RESTORE_SUCCESS": 40
    },
    "THRESHOLDS": {
        "ENTROPY": 3.5,
        "ANOMALY_WINDOW": 10
    }
}

# --- SYSTEM SETTINGS ---
SYSTEM = {
    "MAX_ALERT_LEVEL": 5,
    "MIN_ALERT_LEVEL": 1,
    "RESOURCE_LIMIT_MB": 512
}
