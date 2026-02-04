from typing import List, Dict, Any
from ant_swarm.agents.specialists import SecurityAgent, PerformanceAgent, MaintainabilityAgent
from ant_swarm.core.hive import HiveMind

class Council:
    """
    Upgraded Hive Council.
    Reviews code AND Tool Reports.
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
        Ranks the Top-K options based on Tool Feedback + Mood.
        """
        print(f"\n--- COUNCIL SESSION START (Hive Mood: {self.memory.mood}) ---")

        best_option = None
        best_score = -999

        for opt in options:
            score = 0
            variant = opt['variant_name']
            code = opt['code']
            tools = opt['tool_report']

            print(f"Evaluating Option '{variant}'...")

            # 1. TOOL AUDIT (Automated Veto)
            if not tools['syntax']['valid']:
                print(f"  - VETOED by SyntaxChecker: {tools['syntax']['error']}")
                continue

            if not tools['security']['safe']:
                print(f"  - VETOED by SecurityScanner: {tools['security']['issues']}")
                continue

            # 2. Agent Approval
            vetoed = False
            for agent in self.peers:
                if not agent.review_code(code, task):
                    vetoed = True
                    print(f"  - VETOED by {agent.persona}")
                    break
            if vetoed: continue

            # 3. Scoring
            # Bonus for passing style check
            if tools['style']['compliant']:
                score += 2
            else:
                print(f"  - Style Warnings: {tools['style']['issues']}")
                score -= 1

            if self.memory.mood == "CRITICAL_THINKING":
                if variant == "Safe": score += 5
                if variant == "Balanced": score += 3
            elif self.memory.mood == "UNDER_ATTACK":
                if variant == "Safe": score += 10
            else:
                if variant == "Balanced": score += 5
                if variant == "Fast": score += 2

            print(f"  - Score: {score}")

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
                "reasons": ["All options were vetoed by Tools or Agents."],
                "votes": {}
            }
