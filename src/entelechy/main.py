import asyncio
from entelechy.config import logger
from entelechy.kernel.scheduler import Scheduler
from entelechy.kernel.state_machine import AgentStateMachine
from entelechy.kernel.interfaces import AgentState
from entelechy.cognitive.reasoner import Reasoner
from entelechy.execution.worker import Worker
from entelechy.execution.mcp_client import MCPClient
from entelechy.security.control_plane import ControlPlane
from entelechy.memory.short_term import ShortTermMemory
from entelechy.memory.long_term import LongTermMemory

class EntelechyAOS:
    """The unified Agentic Operating System."""
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.control_plane = ControlPlane()
        self.reasoner = Reasoner()
        self.scheduler = Scheduler()
        # In a real system, the client would point to a real server
        self.mcp_client = MCPClient("http://production-mcp-server")
        self.worker = Worker("primary_worker", self.mcp_client, self.control_plane)
        
        logger.info("Entelechy AOS Initialized")

    async def execute_intent(self, intent: str):
        """Orchestrates an intent-to-outcome workflow."""
        logger.info(f"--- Intent Received: {intent} ---")
        
        # 1. Cognitive: Planning
        plan = self.reasoner.plan_goal(intent)
        self.short_term.set_plan(plan.id, plan)
        logger.info(f"Plan generated with {len(plan.dag)} tasks")
        
        # 2. Kernel: Orchestration
        plan_id = self.scheduler.add_plan(plan)
        
        while not self.scheduler.is_plan_complete(plan_id):
            ready_tasks = self.scheduler.get_ready_tasks(plan_id)
            for task in ready_tasks:
                logger.info(f"Executing: {task.description}")
                
                # Setup security policy for the task (Dynamic Authorization)
                self.control_plane.add_policy(
                    principal=f"Agent::\"{self.worker.worker_id}\"",
                    action="*",
                    resource="*",
                    effect="permit"
                )
                
                # 3. Transition to PLANNING then EXECUTION
                AgentStateMachine.transition(task, AgentState.PLANNING)
                await self.worker.process_task(task)
                
                # 4. Short-term Persistence
                self.short_term.update_task_state(plan.id, task.id, task.status)
                
                if task.status == AgentState.COMMITTED:
                    logger.info(f"Task {task.id} Success")
                elif task.status == AgentState.FAILED:
                    error_msg = task.result.get("error") if task.result else "Unknown error"
                    logger.error(f"Task {task.id} Failed: {error_msg}")
                    return False # Terminate on any failure
                
            if not ready_tasks and not self.scheduler.is_plan_complete(plan_id):
                 # Check if no tasks are ready and not complete - could be an error or dependency issue
                 logger.error("No ready tasks available and plan not complete. Terminating.")
                 return False
            
            await asyncio.sleep(0.1)

        # 5. Outcome: Archival
        if self.scheduler.is_plan_complete(plan_id):
            logger.info("--- Workflow Outcome: SUCCESS ---")
            self.long_term.archive_outcome(intent, "All tasks completed successfully")
            return True
        else:
            logger.error("--- Workflow Outcome: FAILED ---")
            return False

async def main():
    aos = EntelechyAOS()
    await aos.execute_intent("Build a secure communication channel")

if __name__ == "__main__":
    asyncio.run(main())
