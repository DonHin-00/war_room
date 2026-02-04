# Centralized Configuration for Red and Blue Teams

# Hyperparameters
hyperparameters = {
    'learning_rate': 0.001,
    'num_episodes': 1000,
    'discount_factor': 0.99,
}

# Rewards
rewards = {
    'victory': 10,
    'defeat': -10,
    'draw': 5,
}

# Actions
actions = [
    'attack',
    'defend',
    'retreat',
    'gather_information'
]

# File Paths
file_paths = {
    'model_save_path': './models/',
    'log_file_path': './logs/train.log',
}

# Directories
TARGET_DIR = "/tmp/war_zone"
LOG_DIR = "logs"

# Logging Settings
logging_settings = {
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s',
}

# Free Non-API Threat Feeds
# "OCD" Configuration: Strict validation patterns and detailed column mapping
threat_feeds = [
    {
        "name": "URLHaus",
        "url": "https://urlhaus.abuse.ch/downloads/csv_recent/",
        "type": "csv",
        "format": "abuse_ch", # Skip #-prefixed comments
        "columns": {"filename": 2, "hash_sha256": 5},
        "validation": {
            "hash_sha256": r"^[a-fA-F0-9]{64}$",
            "filename": r"^[\w\-. ]+\.[a-zA-Z0-9]{2,4}$" # Basic filename sanity
        }
    },
    {
        "name": "ThreatFox",
        "url": "https://threatfox.abuse.ch/export/csv/recent/",
        "type": "csv",
        "format": "abuse_ch",
        "columns": {"hash_sha256": 2, "filename": 3},
        "validation": {
            "hash_sha256": r"^[a-fA-F0-9]{64}$",
            "filename": r"^[\w\-. ]+\.[a-zA-Z0-9]{2,4}$"
        }
    },
    {
        "name": "MalwareBazaar",
        "url": "https://bazaar.abuse.ch/export/csv/recent/",
        "type": "csv",
        "format": "abuse_ch",
        "columns": {"hash_sha256": 1, "filename": 4, "file_type": 5},
        "validation": {
            "hash_sha256": r"^[a-fA-F0-9]{64}$",
            "file_type": r"^[a-zA-Z0-9]+$"
        }
    }
]
