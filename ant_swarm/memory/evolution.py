import json
import os
import time
from typing import Dict, Any, List

class EvolutionaryMemory:
    """
    Persistent Store for Self-Learning.
    Tracks what works and what fails to guide future evolution.
    """
    def __init__(self, filepath: str = "evolution.json"):
        self.filepath = filepath
        self.history = []
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    self.history = json.load(f)
            except:
                self.history = []

    def _save(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.history, f, indent=2)

    def record_cycle(self, task: str, winner: Dict[str, Any], context: Dict[str, Any]):
        """
        Records a successful cycle.
        """
        entry = {
            "timestamp": time.time(),
            "task_type": task.split()[0] if task else "general", # simplistic taxonomy
            "winning_variant": winner.get("variant_name"),
            "traits": winner.get("traits", {}), # Weights used
            "tool_scores": context.get("scores", {}),
            "hive_mood": context.get("mood", "NEUTRAL")
        }
        self.history.append(entry)
        self._save()

    def get_success_rates(self) -> Dict[str, float]:
        """
        Calculates win rate per variant type.
        """
        counts = {}
        wins = {}

        for entry in self.history:
            v = entry["winning_variant"]
            # Normalize names (handle Hybrid v1.0 etc)
            base_v = v.split()[0]

            wins[base_v] = wins.get(base_v, 0) + 1
            counts[base_v] = counts.get(base_v, 0) + 1

        # Calculate rates? Or just raw counts for weighting
        # Returning normalized weights
        total = len(self.history)
        if total == 0: return {"Safe": 0.33, "Fast": 0.33, "Balanced": 0.33}

        return {k: v / total for k, v in wins.items()}

    def get_optimal_weights(self, task_type: str) -> Dict[str, float]:
        """
        Derives optimal 'paranoia'/'speed' based on history for this task type.
        """
        relevant = [h for h in self.history if h["task_type"] == task_type]
        if not relevant: return None

        # Average the weights of winners
        total_p, total_s = 0, 0
        count = 0
        for r in relevant:
            traits = r.get("traits", {})
            total_p += traits.get("paranoia", 0.5)
            total_s += traits.get("speed", 0.5)
            count += 1

        if count == 0: return None
        return {"paranoia": total_p / count, "speed": total_s / count}
