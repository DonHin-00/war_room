from typing import Dict, Any, List
from apex_framework.core.micro_lm import MicroLM
from apex_framework.memory.hierarchical import SharedMemory

class BaseAgent:
    def __init__(self, name: str, persona: str, memory: SharedMemory):
        self.name = name
        self.persona = persona
        self.memory = memory
        self.lm = MicroLM()

    def process_task(self, task: str, target_file: str = None) -> Dict[str, Any]:
        context = self.memory.retrieve_context(task, target_file)
        result = self.lm.generate(task, self.persona, context)
        self.memory.session.record_change(target_file or "unknown", result['code'], self.name)
        return result

    def review_code(self, code: str, task: str) -> bool:
        if self.persona == "Security" and ("eval" in code or "exec" in code): return False
        if self.persona == "Performance" and "sleep" in code: return False
        if self.persona == "Maintainability" and len(code.split('\n')) > 50: return False
        return True

class SecurityAgent(BaseAgent):
    def __init__(self, memory: SharedMemory):
        super().__init__("SecBot_01", "Security", memory)

class PerformanceAgent(BaseAgent):
    def __init__(self, memory: SharedMemory):
        super().__init__("SpeedBot_99", "Performance", memory)

class MaintainabilityAgent(BaseAgent):
    def __init__(self, memory: SharedMemory):
        super().__init__("CleanCode_v2", "Maintainability", memory)
