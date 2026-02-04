# Centralized Configuration for Red and Blue Teams

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File Paths
Q_TABLE_BLUE = os.path.join(BASE_DIR, "blue_q_table.json")
Q_TABLE_RED = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
WATCH_DIR = "/tmp"
THREAT_FEED_CACHE = os.path.join(BASE_DIR, "threat_feed_cache.json")

# Threat Intelligence
THREAT_FEED_URL_IPS = "https://feodotracker.abuse.ch/downloads/ipblocklist.json"
THREAT_FEED_URL_URLS = "https://urlhaus.abuse.ch/downloads/csv_recent/"

# AI Hyperparameters
ALPHA = 0.4
GAMMA = 0.9
EPSILON_START = 0.3
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995

# Simulation Settings
MAX_ALERT_LEVEL = 5
MIN_ALERT_LEVEL = 1

# Red Team Actions
RED_ACTIONS = ["T1046_RECON", "T1027_OBFUSCATE", "T1003_ROOTKIT", "T1589_LURK", "T1071_C2_BEACON", "T1547_PERSIST"]

# Blue Team Actions
BLUE_ACTIONS = ["SIGNATURE_SCAN", "HEURISTIC_SCAN", "OBSERVE", "IGNORE", "NETWORK_HUNT"]
