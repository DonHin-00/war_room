import random
from typing import List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from ant_swarm.agents.specialists import SecurityAgent, PerformanceAgent, MaintainabilityAgent
from ant_swarm.core.hive import HiveMind
from ant_swarm.tools.toolbox import Toolbox

console = Console()

class WarGames:
    @staticmethod
    def run_simulation(code: str, iterations: int = 50) -> float:
        survived = 0
        # OOOMP: Visual Progress Bar for War Games
        # Only show if not offloaded (Coprocessor handles its own or is silent)
        # But for 'Council' usage, we might want it silent if automated, or visible for demo
        # Let's keep it simple here.
        for _ in range(iterations):
            attack_vector = random.choice(["injection", "dos", "logic_bomb", "fuzzing"])
            if WarGames._survives_attack(code, attack_vector):
                survived += 1
        return survived / iterations

    @staticmethod
    def _survives_attack(code: str, vector: str) -> bool:
        if vector == "injection": return "eval(" not in code and "exec(" not in code
        elif vector == "dos": return "while True" not in code or "sleep" in code
        elif vector == "fuzzing": return "try:" in code
        return True

class Council:
    """
    Upgraded Hive Council with Rich UI.
    """
    def __init__(self, hive: HiveMind):
        self.hive = hive
        self.memory = hive.memory
        self.security = SecurityAgent(self.memory)
        self.performance = PerformanceAgent(self.memory)
        self.maintainability = MaintainabilityAgent(self.memory)
        self.peers = [self.security, self.performance, self.maintainability]

    def select_best_option(self, task: str, options: List[Dict[str, Any]]) -> Dict[str, Any]:
        console.print(f"\n[bold underline]🏛️  COUNCIL SESSION START[/] (DEFCON: {self.memory.defcon})")

        best_option = None
        best_score = -999
        all_scores = {}

        table = Table(title="Option Evaluation Matrix", show_header=True, header_style="bold magenta")
        table.add_column("Variant", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Survival", justify="right")
        table.add_column("Score", justify="right")

        for opt in options:
            score = 0
            variant = opt['variant_name']
            code = opt['code']
            tools = opt['tool_report']

            # 1. TOOL AUDIT
            status = "[green]PASS[/]"
            if not tools['syntax']['valid']: status = "[red]SYNTAX FAIL[/]"
            elif not tools['security']['safe']: status = "[red]SECURITY FAIL[/]"

            survival_prob = 0.0

            if "FAIL" not in status:
                # 2. WAR GAMES
                survival_prob = WarGames.run_simulation(code)
                score += survival_prob * 100

                # Penalize based on DEFCON
                if self.memory.defcon <= 2 and survival_prob < 0.9:
                    status = "[red]TOO RISKY[/]"
                    score = 0
                else:
                     if self.memory.mood == "WAR_ROOM" and variant == "Safe": score += 20

            all_scores[variant] = score

            table.add_row(variant, status, f"{survival_prob:.1%}", f"{score:.1f}")

            if "FAIL" not in status and "RISKY" not in status and score > best_score:
                best_score = score
                best_option = opt

        console.print(table)
        console.print("[bold underline]🏛️  COUNCIL SESSION END[/]\n")

        if best_option:
            self.hive.record_success(task, best_option, {"scores": all_scores, "mood": self.memory.mood})
            return {
                "approved": True,
                "selected_variant": best_option['variant_name'],
                "code": best_option['code'],
                "improvements": best_option.get('improvements', [])
            }
        else:
            return {
                "approved": False,
                "reasons": ["All options failed War Games or Vetoes."],
                "votes": {}
            }
