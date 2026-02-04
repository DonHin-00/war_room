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

# Logging Settings
logging_settings = {
    'log_level': 'INFO',
    'log_format': '%(asctime)s - %(levelname)s - %(message)s',
}

# Free Non-API Threat Feeds
threat_feeds = [
    {
        "name": "URLHaus",
        "url": "https://urlhaus.abuse.ch/downloads/csv_recent/",
        "type": "csv",
        "columns": {"filename": 2, "hash": 5}
    },
    {
        "name": "ThreatFox",
        "url": "https://threatfox.abuse.ch/export/csv/recent/",
        "type": "csv",
        "columns": {"hash": 2, "filename": 3}
    }
]
