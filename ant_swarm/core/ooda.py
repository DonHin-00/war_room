import time
import threading
from ant_swarm.core.hive import SignalBus, HiveState

class OODALoop:
    """
    Observe, Orient, Decide, Act loop for agents.
    """
    def __init__(self, agent_name, cycle_time=1.0):
        self.agent_name = agent_name
        self.cycle_time = cycle_time
        self.bus = SignalBus()
        self.hive = HiveState()
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            observations = self.observe()
            orientation = self.orient(observations)
            decision = self.decide(orientation)
            self.act(decision)
            time.sleep(self.cycle_time)

    def observe(self):
        # Base implementation or override
        return self.hive.get_state()

    def orient(self, observations):
        # Base implementation
        return observations

    def decide(self, orientation):
        # Base implementation
        return None

    def act(self, decision):
        # Base implementation
        pass
