from typing import Dict, Any, Optional
from entelechy.config import logger
from entelechy.kernel.interfaces import AgentPlan, AgentState

class ShortTermMemory:
    """Simulates a fast key-value store (e.g., Redis) for active state management."""
    
    def __init__(self):
        self._storage: Dict[str, Any] = {}
        logger.info("Short-Term Memory (Redis Sim) initialized")

    def set_plan(self, plan_id: str, plan: AgentPlan):
        """Stores an active agent plan."""
        self._storage[f"plan:{plan_id}"] = plan.model_dump_json()
        logger.debug(f"Plan {plan_id} persisted to short-term memory")

    def get_plan(self, plan_id: str) -> Optional[AgentPlan]:
        """Retrieves an active agent plan."""
        data = self._storage.get(f"plan:{plan_id}")
        if data:
            return AgentPlan.model_validate_json(data)
        return None

    def update_task_state(self, plan_id: str, task_id: str, state: AgentState):
        """Updates the state of a specific task in a plan."""
        plan = self.get_plan(plan_id)
        if plan:
            for node in plan.dag:
                if node.id == task_id:
                    node.status = state
                    self.set_plan(plan_id, plan)
                    return True
        return False

    def clear(self):
        """Clears all short-term state."""
        self._storage.clear()
        logger.info("Short-term memory cleared")
