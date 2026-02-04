#!/usr/bin/env python3
"""
Red Brain (APT Edition)
Uses Advanced Tools for realistic emulation.
"""

import time
import random
import logging
import threading
from threat_intel import ThreatIntel
from red_tools import TrafficGenerator, DGA, PersistenceManager
from db_manager import DatabaseManager
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RED APT] - %(message)s')

class RedAPT:
    def __init__(self):
        self.db = DatabaseManager()
        self.ti = ThreatIntel() # Relies on DB now
        self.traffic = TrafficGenerator()
        self.dga = DGA()
        self.persist = PersistenceManager()
        self.running = True

    def run(self):
        logging.info("Red APT Initialized. Entering Stealth Mode.")

        while self.running:
            try:
                # 1. Traffic Generation (Beaconing)
                # 30% chance to beacon
                if random.random() < 0.3:
                    target_ip = self.ti.get_c2_ip()
                    if target_ip:
                        logging.info(f"Sending HTTP Beacon to {target_ip}")
                        self.traffic.send_http_beacon(target_ip)
                        self.db.log_event("RED", "BEACON", f"Target: {target_ip}")

                # 2. DGA (DNS Noise)
                # 20% chance to resolve random domain
                if random.random() < 0.2:
                    domain = self.dga.generate_domain()
                    logging.info(f"DGA Resolution Attempt: {domain}")
                    self.dga.resolve_domain(domain)
                    self.db.log_event("RED", "DGA", domain)

                # 3. Persistence
                # 5% chance to drop persistence if not already established
                if random.random() < 0.05:
                    method = random.choice(["cron", "bashrc"])
                    if method == "cron":
                        self.persist.install_cron()
                        logging.info("Installed Cron Persistence")
                    else:
                        self.persist.install_bashrc()
                        logging.info("Installed Bashrc Persistence")
                    self.db.log_event("RED", "PERSIST", method)

                # 4. Sleep (Jitter)
                # Random sleep 1-5 seconds
                time.sleep(random.uniform(1.0, 5.0))

            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logging.error(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    apt = RedAPT()
    apt.run()
