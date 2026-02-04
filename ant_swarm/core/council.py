from typing import List, Dict, Any
from ant_swarm.agents.specialists import SecurityAgent, PerformanceAgent, MaintainabilityAgent
from ant_swarm.memory.hierarchical import SharedMemory

class Council:
    def __init__(self, memory: SharedMemory):
        self.memory = memory
        self.security = SecurityAgent(memory)
        self.performance = PerformanceAgent(memory)
        self.maintainability = MaintainabilityAgent(memory)
        self.peers = [self.security, self.performance, self.maintainability]

    def debate_pr(self, task: str, proposed_code: str) -> Dict[str, Any]:
        """
        The "Council of Peers" Debate.
        All three agents must approve the code.
        """
        votes = {}
        rejected = False
        rejection_reasons = []

        print("\n--- COUNCIL SESSION START ---")
        for agent in self.peers:
            vote = agent.review_code(proposed_code, task)
            votes[agent.persona] = vote
            if vote:
                print(f"[{agent.persona}] APPROVED")
            else:
                print(f"[{agent.persona}] REJECTED")
                rejected = True
                rejection_reasons.append(f"{agent.persona} objected to the implementation.")

        print("--- COUNCIL SESSION END ---\n")

        if rejected:
            return {
                "approved": False,
                "reasons": rejection_reasons,
                "votes": votes
            }
        else:
            return {
                "approved": True,
                "reasons": [],
                "votes": votes
            }
