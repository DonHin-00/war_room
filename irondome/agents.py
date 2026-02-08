import time
import os
import json
from .siem import siem_logger

class LogAgent:
    def __init__(self, log_file):
        self.log_file = log_file
        self.last_pos = 0

    def run_loop(self):
        print(f"LogAgent watching {self.log_file}")
        while True:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    f.seek(self.last_pos)
                    lines = f.readlines()
                    self.last_pos = f.tell()

                    for line in lines:
                        if "WARNING" in line:
                            siem_logger.log_event("LogAgent", "APP_WARNING", line.strip(), "WARNING")
                        if "ERROR" in line:
                            siem_logger.log_event("LogAgent", "APP_ERROR", line.strip(), "CRITICAL")
                        if "Transfer successful" in line:
                            siem_logger.log_event("LogAgent", "MONEY_MOVE", line.strip(), "INFO")
            time.sleep(1)
