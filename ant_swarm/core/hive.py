import time
from typing import Dict, Any, List, Callable
from collections import defaultdict
from ant_swarm.memory.hierarchical import SharedMemory

class Signal:
    def __init__(self, type: str, data: Any, source: str):
        self.type = type
        self.data = data
        self.source = source
        self.timestamp = time.time()

class HiveState(SharedMemory):
    """
    Intricate Global State with Military Logic.
    """
    def __init__(self):
        super().__init__()
        self.mood = "NEUTRAL"
        self.defcon = 5 # 5=Peace, 1=War
        self.threat_matrix = {
            "complexity_level": 0, # From RevEng
            "active_vulnerabilities": 0, # From SecurityScanner
            "hostile_signals": 0,
            "active_decoys": 0 # From Mirage
        }
        self.active_signals = []

    def set_defcon(self, level: int):
        level = max(1, min(5, level))
        if self.defcon != level:
            print(f"[HIVE STATE] 🚨 DEFCON CHANGED: {self.defcon} -> {level}")
            self.defcon = level
            self._update_mood_from_defcon()

    def update_threat_matrix(self, key: str, value: int):
        self.threat_matrix[key] = value
        self._assess_defcon()

    def _assess_defcon(self):
        """
        Deep ML Logic: Heuristic Assessment of Threat Matrix to set DEFCON.
        """
        score = 0
        score += self.threat_matrix["complexity_level"] * 0.1
        score += self.threat_matrix["active_vulnerabilities"] * 2.0
        score += self.threat_matrix["hostile_signals"] * 1.5

        previous_defcon = self.defcon
        if score > 10: self.set_defcon(1)
        elif score > 5: self.set_defcon(3)
        elif score > 2: self.set_defcon(4)
        else: self.set_defcon(5)

    def _update_mood_from_defcon(self):
        moods = {
            5: "PEACE_TIME",
            4: "VIGILANT",
            3: "ELEVATED_RISK",
            2: "HIGH_ALERT",
            1: "WAR_ROOM"
        }
        self.mood = moods[self.defcon]

    def set_mood(self, mood: str):
        self.mood = mood

class SignalBus:
    """
    The Nervous System of the Hive.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable[[Signal], None]]] = defaultdict(list)

    def subscribe(self, signal_type: str, callback: Callable[[Signal], None]):
        self.subscribers[signal_type].append(callback)

    def publish(self, signal: Signal):
        print(f"[SIGNAL BUS] 📡 Broadcasting {signal.type} from {signal.source}")
        if signal.type in self.subscribers:
            for callback in self.subscribers[signal.type]:
                callback(signal)

class HiveMind:
    """
    The Central Orchestrator.
    Now supports Hanging Off Modules (Mirage).
    """
    def __init__(self):
        self.memory = HiveState()
        self.bus = SignalBus()
        self.mirage = None # To be attached

    def attach_mirage(self, mirage_layer):
        print("[HIVE] 🔗 Attaching Deception Module (Mirage Layer)...")
        self.mirage = mirage_layer

    def broadcast(self, type: str, data: Any, source: str):
        sig = Signal(type, data, source)
        self.bus.publish(sig)
        self.memory.active_signals.append(sig)
