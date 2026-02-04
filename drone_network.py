
import os
import time
import random
import utils
import logging

class Drone:
    def __init__(self, drone_id, sector_root):
        self.id = drone_id
        self.sector_root = sector_root
        self.status = "IDLE"

    def log(self, message):
        print(f"\033[90m[DRONE-{self.id}] {message}\033[0m")

    def patrol(self):
        pass

class SentryDrone(Drone):
    """Mobile Eyes: Scans sectors for threats and updates Intel DB."""
    def patrol(self):
        self.status = "SCANNING"
        # Pick a random subdirectory or root
        target_dir = self.sector_root
        try:
            subdirs = [f.path for f in os.scandir(self.sector_root) if f.is_dir()]
            if subdirs:
                target_dir = random.choice(subdirs)
        except: pass

        self.log(f"Scanning sector: {os.path.basename(target_dir)}")
        visible, hidden = utils.scan_threats(target_dir)

        found = 0
        for threat in visible + hidden:
            # Report to DB
            f_hash = utils.calculate_sha256(threat)
            if f_hash:
                utils.DB.add_threat("hash", f_hash, source=f"DRONE-{self.id}")
                found += 1

        if found > 0:
            self.log(f"Reported {found} threats to Central Command.")

class HoneyDrone(Drone):
    """Pure Honeypot Essence: Deploys traps and monitors access."""
    def __init__(self, drone_id, sector_root):
        super().__init__(drone_id, sector_root)
        self.decoy_path = None

    def deploy(self):
        self.status = "DEPLOYING"
        filename = f"secret_drone_logs_{random.randint(1000,9999)}.txt"
        self.decoy_path = os.path.join(self.sector_root, filename)
        try:
            utils.safe_file_write(self.decoy_path, "CONFIDENTIAL DRONE TELEMETRY\n")
            self.log(f"Deployed decoy: {filename}")
        except: pass

    def monitor(self):
        if not self.decoy_path or not os.path.exists(self.decoy_path):
            self.deploy()
            return

        try:
            # Check if accessed (atime > mtime usually implies read)
            stat = os.stat(self.decoy_path)
            if stat.st_atime > stat.st_mtime + 1.0: # 1s buffer
                self.log(f"ALERT! Decoy accessed! Tracing...")
                # Update War State to High Alert
                current = utils.DB.get_state("blue_alert_level", 1)
                utils.DB.set_state("blue_alert_level", min(5, current + 1))
                # Reset decoy
                os.utime(self.decoy_path, None)
        except: pass

    def patrol(self):
        self.monitor()

class DroneSwarm:
    def __init__(self, count, sector_root):
        self.drones = []
        for i in range(count):
            if i % 2 == 0:
                self.drones.append(SentryDrone(i, sector_root))
            else:
                self.drones.append(HoneyDrone(i, sector_root))

    def activate(self):
        for drone in self.drones:
            drone.patrol()
