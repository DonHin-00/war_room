import os

# --- SYSTEM CONFIGURATION ---
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
WAR_ZONE_DIR: str = os.environ.get("WAR_ZONE_DIR", "/tmp")
CRITICAL_DIR: str = os.path.join(WAR_ZONE_DIR, "critical")

# --- FILE PATHS ---
Q_TABLE_BLUE = os.path.join(BASE_DIR, "blue_q_table.json")
Q_TABLE_RED = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
SIGNATURE_FILE = os.path.join(BASE_DIR, "signatures.json")
AUDIT_LOG = os.path.join(BASE_DIR, "audit.jsonl")
TRACE_LOG = os.path.join(BASE_DIR, "trace.jsonl")
INCIDENT_DIR = os.path.join(BASE_DIR, "incidents")

# --- BLUE TEAM CONFIG ---
BLUE_ACTIONS = [
    "SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE",
    "DEPLOY_DECOY", "DEPLOY_TRAP", "BACKUP_CRITICAL", "RESTORE_CRITICAL"
]
BLUE_REWARDS = {
    'MITIGATION': 25,
    'PATIENCE': 10,
    'WASTE': -15,
    'NEGLIGENCE': -50,
    'HONEYPOT_TRIGGERED': 100, # Massive reward for trapping Red
    'RESTORE_SUCCESS': 30,
    'FIM_ALERT': 50
}

# --- RED TEAM CONFIG ---
RED_ACTIONS = [
    "T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK",
    "T1071_C2_BEACON", "T1486_ENCRYPT", "T1547_PERSISTENCE", "T1041_EXFILTRATION",
    "T1091_REPLICATION", "T1190_EXPLOIT", "T1204_USER_EXECUTION", "T1048_EXFIL_ALT"
]
RED_REWARDS = {
    'IMPACT': 10,
    'STEALTH': 15,
    'CRITICAL': 30,
    'C2_SUCCESS': 50,
    'RANSOM_SUCCESS': 60,
    'PERSISTENCE_SUCCESS': 40,
    'EXFIL_SUCCESS': 80,
    'REPLICATION_SUCCESS': 70,
    'EXPLOIT_SUCCESS': 90,
    'TRAPPED': -50 # Penalty for hitting a honeypot
}

# --- COMMON AI CONFIG ---
# Tune these parameters to adjust how "Smart" the bots are.
AI_PARAMS = {
    'ALPHA': 0.1,           # Learning Rate: How fast they adapt to new info (0.0 = never learn, 1.0 = forget old).
    'ALPHA_DECAY': 0.9999,  # Decay rate for learning (stabilizes over time).
    'GAMMA': 0.95,          # Discount Factor: Importance of future rewards (0.0 = short-sighted, 1.0 = long-term planner).
    'EPSILON_START': 0.5,   # Exploration Rate: Chance to try random actions vs known best strategies.
    'EPSILON_DECAY': 0.995, # How quickly they shift from Exploration to Exploitation.
    'MIN_EPSILON': 0.02,    # Minimum randomness to keep them creative.
    'SYNC_INTERVAL': 10,    # How often to persist learned knowledge (Q-Tables) to disk.
    'MEMORY_SIZE': 1000,    # Experience Replay Buffer Size (not currently used in tabular Q-learning but reserved).
    'BATCH_SIZE': 32        # Batch size for learning optimization.
}

# --- ALERT LEVELS ---
MAX_ALERT = 5
MIN_ALERT = 1

# Ensure directories exist
if not os.path.exists(INCIDENT_DIR):
    try:
        os.makedirs(INCIDENT_DIR)
    except: pass
