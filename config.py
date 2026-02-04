import os

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BATTLEFIELD_ROOT = os.path.join(BASE_DIR, "battlefield")
DATA_DIR = os.path.join(BASE_DIR, "simulation_data")
INCIDENT_DIR = os.path.join(DATA_DIR, "incidents")

# Network Zones (Segregated Environment)
ZONES = {
    "DMZ": os.path.join(BATTLEFIELD_ROOT, "dmz"),
    "USER": os.path.join(BATTLEFIELD_ROOT, "user"),
    "SERVER": os.path.join(BATTLEFIELD_ROOT, "server"),
    "CORE": os.path.join(BATTLEFIELD_ROOT, "core"),
}

# Process Directory (Simulated RAM)
PROC_DIR = os.path.join(BASE_DIR, ".proc")

PATHS = {
    "BASE_DIR": BASE_DIR,
    "WAR_ZONE": BATTLEFIELD_ROOT,
    "ZONES": ZONES,
    "PROC": PROC_DIR,
    "DATA_DIR": DATA_DIR,
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
        "T1486_ENCRYPT",
        "T1071_C2_BEACON",
        "T1055_INJECTION",
        "T1070_WIPE_LOGS",
        "T1021_LATERAL_MOVE" # New Action
    ],
    "REWARDS": {
        "IMPACT": 10,
        "STEALTH": 15,
        "CRITICAL": 50, # Higher reward for CORE access
        "PENALTY_TRAPPED": -20,
        "PERSISTENCE": 25,
        "LATERAL_SUCCESS": 20
    }
}

# --- BLUE TEAM CONFIG ---
BLUE = {
    "LAYERS": ["SENSOR", "ANALYZER", "HUNTER", "RESPONDER"],
    "ACTIONS": [
        "SIGNATURE_SCAN",
        "HEURISTIC_SCAN",
        "OBSERVE",
        "IGNORE",
        "DEPLOY_TRAP",
        "DEPLOY_DECOY",
        "BACKUP_CRITICAL",
        "RESTORE_DATA",
        "HUNT_PROCESSES",
        "VERIFY_INTEGRITY",
        "ISOLATE_ZONE" # New Action
    ],
    "REWARDS": {
        "MITIGATION": 25,
        "PATIENCE": 10,
        "TRAP_SUCCESS": 50,
        "PENALTY_WASTE": -15,
        "PENALTY_NEGLIGENCE": -50,
        "ANOMALY_BONUS": 20,
        "RESTORE_SUCCESS": 40,
        "INTEGRITY_BONUS": 15,
        "ISOLATION_BONUS": 30
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
    "RESOURCE_LIMIT_MB": 512,
    "CPU_LIMIT_SECONDS": 600
}
