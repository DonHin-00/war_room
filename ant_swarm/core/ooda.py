from typing import Dict, Any, List
from ant_swarm.core.hive import HiveMind

class TacticalDoctrine:
    """
    Defines the Rules of Engagement based on OODA analysis.
    """
    def __init__(self, name: str, weights: Dict, constraints: List[str]):
        self.name = name
        self.weights = weights # e.g. paranoia, speed
        self.constraints = constraints

class OODALoop:
    """
    The Decision Engine: Observe, Orient, Decide, Act.
    """
    def __init__(self, hive: HiveMind):
        self.hive = hive

    def execute_cycle(self, task: str) -> TacticalDoctrine:
        # 1. OBSERVE
        defcon = self.hive.memory.defcon
        threats = self.hive.memory.threat_matrix

        # 2. ORIENT
        context_score = threats['active_vulnerabilities'] * 2 + (6 - defcon)

        # 3. DECIDE
        if defcon <= 2:
            return self._doctrine_iron_dome()
        elif defcon <= 3:
            return self._doctrine_active_defense()
        elif threats['complexity_level'] > 50:
            return self._doctrine_refactor()
        else:
            return self._doctrine_rapid_dev()

        # 4. ACT is handled by the caller (MicroLM) using this doctrine

    def _doctrine_iron_dome(self):
        return TacticalDoctrine(
            name="Iron Dome",
            weights={"paranoia": 1.0, "speed": 0.1},
            constraints=["NO_EXTERNAL_LIBS", "STRICT_TYPE_HINTS", "MAX_LINES_20"]
        )

    def _doctrine_active_defense(self):
        return TacticalDoctrine(
            name="Active Defense",
            weights={"paranoia": 0.8, "speed": 0.4},
            constraints=["NO_EVAL", "AUDIT_LOGGING_REQUIRED"]
        )

    def _doctrine_rapid_dev(self):
        return TacticalDoctrine(
            name="Rapid Deployment",
            weights={"paranoia": 0.3, "speed": 0.9},
            constraints=["NO_BLOCKING_IO"]
        )

    def _doctrine_refactor(self):
         return TacticalDoctrine(
            name="Structural Reform",
            weights={"paranoia": 0.5, "speed": 0.5},
            constraints=["MAX_COMPLEXITY_10", "DOCSTRINGS_REQUIRED"]
        )
