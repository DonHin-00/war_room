import time
from typing import Dict, Any, List, Callable
from collections import defaultdict
from ant_swarm.memory.hierarchical import SharedMemory
from ant_swarm.memory.evolution import EvolutionaryMemory

class Signal:
    def __init__(self, type: str, data: Any, source: str):
        self.type = type
        self.data = data
        self.source = source
        self.timestamp = time.time()

class HiveState(SharedMemory):
    def __init__(self):
        super().__init__()
        self.mood = "NEUTRAL"
        self.defcon = 5
        self.threat_matrix = {
            "complexity_level": 0,
            "active_vulnerabilities": 0,
            "hostile_signals": 0,
            "active_decoys": 0
        }
        self.active_signals = []
        self.learned_bias = {"paranoia": 0.0, "speed": 0.0}

    def set_defcon(self, level: int):
        level = max(1, min(5, level))
        if self.defcon != level:
            print(f"[HIVE STATE] 🚨 DEFCON CHANGED: {self.defcon} -> {level}")
            self.defcon = level
            self._update_mood_from_defcon()

    def update_threat_matrix(self, key: str, value: int):
        self.threat_matrix[key] = value
        self._assess_defcon()

    def apply_learning(self, weights: Dict[str, float]):
        if weights:
            print(f"[HIVE STATE] 🧠 Integrating Learned Wisdom: {weights}")
            self.learned_bias = weights

    def _assess_defcon(self):
        score = 0
        score += self.threat_matrix["complexity_level"] * 0.1
        score += self.threat_matrix["active_vulnerabilities"] * 2.0
        score += self.threat_matrix["hostile_signals"] * 1.5

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
    NOW WITH EXTERNAL SUPPORT MODULES (Hanging Off).
    """
    def __init__(self):
        self.memory = HiveState()
        self.bus = SignalBus()
        self.evolution = EvolutionaryMemory()
        self.mirage = None

        # Support Modules
        self.storage = None
        self.coprocessor = None
        self.gatekeeper = None

    def attach_mirage(self, mirage_layer):
        print("[HIVE] 🔗 Attaching Deception Module (Mirage Layer)...")
        self.mirage = mirage_layer

    def attach_support(self, storage, coprocessor, gatekeeper):
        print("[HIVE] 🔗 Attaching External Support Modules (Storage, Coprocessor, Gatekeeper)...")
        self.storage = storage
        self.coprocessor = coprocessor
        self.gatekeeper = gatekeeper

    def broadcast(self, type: str, data: Any, source: str):
        sig = Signal(type, data, source)
        self.bus.publish(sig)
        self.memory.active_signals.append(sig)

    def autotune(self):
        print("[HIVE] 🧬 Initiating Meta-Learning Autotune...")
        optimal = self.evolution.get_optimal_weights("login")
        if optimal:
            self.memory.apply_learning(optimal)
        else:
            print("[HIVE] Not enough data to evolve yet.")

    def record_success(self, task: str, winner: Dict, context: Dict):
        # 1. Save to Evolution (JSON)
        self.evolution.record_cycle(task, winner, context)

        # 2. Save to External Storage (SQLite) if available
        if self.storage:
            self.storage.save_war_story(task, winner.get("code", ""), 0.99) # Mock rate for now
