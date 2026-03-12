from typing import List, Dict, Optional
from entelechy.kernel.interfaces import TaskNode, AgentState, AgentPlan
from entelechy.kernel.state_machine import AgentStateMachine
from entelechy.config import logger

class Scheduler:
    """Orchestrates task execution according to a Directed Acyclic Graph (DAG)."""
    
    def __init__(self):
        self.active_plans: Dict[str, AgentPlan] = {}

    def add_plan(self, plan: AgentPlan):
        """Adds a new plan to the scheduler."""
        # Simple ID for the plan for now
        plan_id = f"plan_{len(self.active_plans) + 1}"
        self.active_plans[plan_id] = plan
        logger.info(f"New plan added: {plan_id} with goal: {plan.goal}")
        return plan_id

    def get_ready_tasks(self, plan_id: str) -> List[TaskNode]:
        """Returns tasks that have all dependencies met and are in PENDING state."""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return []
            
        ready_tasks = []
        completed_task_ids = {node.id for node in plan.dag if node.status == AgentState.COMMITTED}
        
        for node in plan.dag:
            if node.status == AgentState.PENDING:
                if all(dep_id in completed_task_ids for dep_id in node.dependencies):
                    ready_tasks.append(node)
                    
        return ready_tasks

    def update_task_status(self, plan_id: str, task_id: str, next_state: AgentState, result: Optional[dict] = None):
        """Updates the status of a specific task within a plan."""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return False
            
        for node in plan.dag:
            if node.id == task_id:
                if next_state == AgentState.COMMITTED:
                    AgentStateMachine.commit_task(node, result)
                elif next_state == AgentState.FAILED:
                    AgentStateMachine.fail_task(node, result.get("error") if result else "Unknown error")
                else:
                    AgentStateMachine.transition(node, next_state)
                return True
        return False

    def is_plan_complete(self, plan_id: str) -> bool:
        """Checks if all tasks in a plan are committed."""
        plan = self.active_plans.get(plan_id)
        if not plan:
            return False
        return all(node.status == AgentState.COMMITTED for node in plan.dag)
