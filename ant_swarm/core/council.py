import random
from typing import List, Dict, Any
from ant_swarm.agents.specialists import SecurityAgent, PerformanceAgent, MaintainabilityAgent
from ant_swarm.core.hive import HiveMind
from ant_swarm.tools.toolbox import Toolbox

class WarGames:
    """
    Simulates attacks to determine survival probability.
    """
    @staticmethod
    def run_simulation(code: str, iterations: int = 50) -> float:
        """
        Runs a Monte Carlo Lite simulation.
        Returns a survival probability (0.0 - 1.0).
        """
        survived = 0
        for _ in range(iterations):
            # Simulate random attack vectors
            attack_vector = random.choice(["injection", "dos", "logic_bomb", "fuzzing"])

            if WarGames._survives_attack(code, attack_vector):
                survived += 1

        return survived / iterations

    @staticmethod
    def _survives_attack(code: str, vector: str) -> bool:
        # Heuristic simulation logic
        if vector == "injection":
            return "eval(" not in code and "exec(" not in code
        elif vector == "dos":
            return "while True" not in code or "sleep" in code
        elif vector == "fuzzing":
            return "try:" in code # Error handling helps survival
        return True

class Council:
    """
    Upgraded Hive Council with War Games.
    """
    def __init__(self, hive: HiveMind):
        self.hive = hive
        self.memory = hive.memory
        self.security = SecurityAgent(self.memory)
        self.performance = PerformanceAgent(self.memory)
        self.maintainability = MaintainabilityAgent(self.memory)
        self.peers = [self.security, self.performance, self.maintainability]

    def select_best_option(self, task: str, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Ranks options using War Games Simulation.
        """
        print(f"\n--- COUNCIL SESSION START (DEFCON: {self.memory.defcon}) ---")

        best_option = None
        best_score = -999

        for opt in options:
            score = 0
            variant = opt['variant_name']
            code = opt['code']
            tools = opt['tool_report']

            print(f"Evaluating Option '{variant}'...")

            # 1. TOOL AUDIT (Automated Veto)
            if not tools['syntax']['valid']: continue
            if not tools['security']['safe']: continue

            # 2. WAR GAMES SIMULATION
            survival_prob = WarGames.run_simulation(code)
            print(f"  - War Games Survival Rate: {survival_prob:.1%}")

            # 3. SCORING
            score += survival_prob * 100

            # Penalize based on DEFCON requirements
            if self.memory.defcon <= 2 and survival_prob < 0.9:
                print(f"  - REJECTED: Survival rate too low for DEFCON {self.memory.defcon}")
                continue

            # Mood/Doctrine alignment
            if self.memory.mood == "WAR_ROOM" and variant == "Safe": score += 20

            print(f"  - Final Score: {score:.1f}")

            if score > best_score:
                best_score = score
                best_option = opt

        print("--- COUNCIL SESSION END ---\n")

        if best_option:
            return {
                "approved": True,
                "selected_variant": best_option['variant_name'],
                "code": best_option['code']
            }
        else:
            return {
                "approved": False,
                "reasons": ["All options failed War Games or Vetoes."],
                "votes": {}
            }
