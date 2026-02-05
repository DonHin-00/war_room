import threading
import json
import time
import logging

logger = logging.getLogger("HiveMind")

class SignalBus:
    _instance = None
    _lock = threading.Lock()
    _subscribers = {}

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SignalBus, cls).__new__(cls)
                    cls._instance._subscribers = {}
        return cls._instance

    def subscribe(self, event_type, callback):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
        logger.debug(f"Subscribed to {event_type}")

    def publish(self, event_type, data=None):
        logger.debug(f"Publishing {event_type}: {data}")
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in subscriber for {event_type}: {e}")

class HiveState:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(HiveState, cls).__new__(cls)
                    cls._instance.state = {
                        "defcon": 5,
                        "mood": "NEUTRAL",
                        "active_threats": [],
                        "blue_level": 1,
                        "red_level": 1
                    }
        return cls._instance

    def update_defcon(self, level):
        with self._lock:
            self.state["defcon"] = level
            SignalBus().publish("DEFCON_CHANGE", level)

    def update_mood(self, mood):
        with self._lock:
            self.state["mood"] = mood
            SignalBus().publish("MOOD_CHANGE", mood)

    def get_state(self):
        with self._lock:
            return self.state.copy()

    def set_threats(self, threats):
        with self._lock:
            self.state["active_threats"] = threats
            SignalBus().publish("THREAT_UPDATE", threats)
