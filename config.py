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

# Ensure directories exist (Config should probably not do side effects, but for simplicity we keep it)
# We moved creation to simulation_runner, but paths are needed.

PATHS = {
    "BASE_DIR": BASE_DIR,
    "WAR_ZONE": BATTLEFIELD_ROOT,
    "ZONES": ZONES,
    "PROC": PROC_DIR,
    "DATA_DIR": DATA_DIR,
    "WAR_STATE": os.path.join(DATA_DIR, "war_state.json"),
    "SIGNATURES": os.path.join(DATA_DIR, "signatures.json"),
    "AUDIT_LOG": os.path.join(DATA_DIR, "audit.jsonl"),
    "INCIDENTS": INCIDENT_DIR,
    "LOG_RED": os.path.join(BASE_DIR, "red.log"),
    "LOG_BLUE": os.path.join(BASE_DIR, "blue.log"),
    "LOG_MAIN": os.path.join(BASE_DIR, "war_room.log"),
}

# --- EMULATION PROBABILITIES ---
# Weights for random.choices
EMULATION = {
    "RED": {
        "DMZ": {
            "T1046_RECON": 0.3,
            "T1071_C2_BEACON": 0.3,
            "T1036_MASQUERADE": 0.2,
            "T1021_LATERAL_MOVE": 0.2
        },
        "USER": {
            "T1027_OBFUSCATE": 0.3,
            "T1589_LURK": 0.2,
            "T1055_INJECTION": 0.2,
            "T1021_LATERAL_MOVE": 0.3
        },
        "SERVER": {
            "T1003_ROOTKIT": 0.4,
            "T1070_WIPE_LOGS": 0.2,
            "T1021_LATERAL_MOVE": 0.4
        },
        "CORE": {
            "T1486_ENCRYPT": 0.6,
            "T1070_WIPE_LOGS": 0.3,
            "T1589_LURK": 0.1
        }
    },
    "BLUE": {
        # Frequency (every N ticks)
        "SENSOR_FREQ": 1,
        "ANALYZER_FREQ": 3,
        "HUNTER_FREQ": 5,
        "RESPONDER_FREQ": 1 # Always check for needed response
    }
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
        "T1021_LATERAL_MOVE"
    ],
    "REWARDS": {
        # Kept for scoring/logging, though not used for learning
        "IMPACT": 10,
        "CRITICAL": 50,
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
        "ISOLATE_ZONE"
    ],
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
