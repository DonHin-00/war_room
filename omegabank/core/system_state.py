import threading
import time

class SystemState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SystemState, cls).__new__(cls)
                    cls._instance._init()
        return cls._instance

    def _init(self):
        self.defcon = 1 # 1 (Peace) to 5 (War)
        self.rate_limit_multiplier = 1.0 # 1.0 = Standard, 0.1 = Strict
        self.active_honeypots = False

        # Metrics
        self.total_requests = 0
        self.blocked_requests = 0
        self.ai_blue_action = "IDLE"
        self.ai_red_action = "IDLE"
        self.red_success_rate = 0.0

    def update_metrics(self, blocked=False):
        self.total_requests += 1
        if blocked:
            self.blocked_requests += 1

    def get_threat_level(self):
        # Calculate localized threat score 0-100
        if self.total_requests == 0: return 0
        ratio = self.blocked_requests / self.total_requests
        return min(100, int(ratio * 100))

# Global Singleton
system_state = SystemState()
