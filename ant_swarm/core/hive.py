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
    Intricate Global State with Moods.
    """
    def __init__(self):
        super().__init__()
        self.mood = "NEUTRAL"
        self.active_signals = []

    def set_mood(self, mood: str):
        print(f"[HIVE STATE] Mood shifting from {self.mood} to {mood}")
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
    """
    def __init__(self):
        self.memory = HiveState()
        self.bus = SignalBus()

    def broadcast(self, type: str, data: Any, source: str):
        sig = Signal(type, data, source)
        self.bus.publish(sig)
        self.memory.active_signals.append(sig)
