# Centralized Configuration for Red and Blue Teams

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# File Paths
DB_PATH = os.path.join(BASE_DIR, "simulation.db")
Q_TABLE_BLUE = os.path.join(BASE_DIR, "blue_q_table.json")
Q_TABLE_RED = os.path.join(BASE_DIR, "red_q_table.json")
STATE_FILE = os.path.join(BASE_DIR, "war_state.json")
WATCH_DIR = "/tmp"
THREAT_FEED_CACHE = os.path.join(BASE_DIR, "threat_feed_cache.json")

# Threat Intelligence Sources (Free, No API Key, Live)
# 15+ Feeds including Aggregators, Botnet Trackers, and Phishing Lists
THREAT_FEEDS = {
    "Feodo_Tracker": "https://feodotracker.abuse.ch/downloads/ipblocklist.json",
    "CINS_Army": "http://cinsscore.com/list/ci-badguys.txt",
    "GreenSnow": "https://blocklist.greensnow.co/greensnow.txt",
    "Blocklist_DE": "https://lists.blocklist.de/lists/all.txt",
    "DigitalSide": "https://osint.digitalside.it/Threat-Intel/lists/latestips.txt",
    "EmergingThreats": "https://rules.emergingthreats.net/blockrules/compromised-ips.txt",
    "BinaryDefense": "https://www.binarydefense.com/banlist.txt",
    "IPSum_Aggregator": "https://raw.githubusercontent.com/stamparm/ipsum/master/ipsum.txt",
    "Tor_Exit_Nodes": "https://check.torproject.org/torbulkexitlist",
    "URLHaus": "https://urlhaus.abuse.ch/downloads/hostfile/",
    "ThreatFox": "https://threatfox.abuse.ch/export/json/recent/",
    "MalwareBazaar": "https://bazaar.abuse.ch/export/txt/sha256/recent/", # Hashes, treated differently or just logged
    "Botvrij_IOC": "https://www.botvrij.eu/data/ioclist.ip-dst",
    "SANS_Top20": "https://isc.sans.edu/feeds/suspiciousdomains_High.txt", # Domains
    "OpenPhish": "https://openphish.com/feed.txt",
    "Bambenek_C2": "https://osint.bambenekconsulting.com/feeds/c2-ipmasterlist.txt"
}

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
