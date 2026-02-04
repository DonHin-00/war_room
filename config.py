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
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
SIGNATURE_DB = os.path.join(BASE_DIR, "signatures.json")
SESSION_DB = os.path.join(BASE_DIR, "sessions.json")
TOPOLOGY_FILE = os.path.join(BASE_DIR, "topology.json")

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
