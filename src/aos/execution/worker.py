from typing import Optional
from aos.kernel.interfaces import TaskNode, AgentState
from aos.kernel.state_machine import AgentStateMachine
from aos.execution.mcp_client import MCPClient
from aos.config import logger

class Worker:
    """Represents a worker agent that performs physical work via tools."""
    
    def __init__(self, worker_id: str, mcp_client: MCPClient):
        self.worker_id = worker_id
        self.mcp_client = mcp_client
        self.current_task: Optional[TaskNode] = None

    async def process_task(self, task: TaskNode) -> TaskNode:
        """Processes a task assigned by the Kernel."""
        self.current_task = task
        logger.info(f"Worker {self.worker_id} processing task {task.id}: {task.description}")
        
        # 1. State: CLAIMED (handled by Kernel, but worker acknowledges)
        AgentStateMachine.transition(task, AgentState.EXECUTING)
        
        # 2. Logic: Mocking tool selection based on description
        # In a real system, the Cognitive layer would specify the tool
        tool_name = "google_search" if "search" in task.description.lower() else "read_file"
        args = {"query": task.description} if tool_name == "google_search" else {"path": "data.txt"}
        
        # 3. Execution
        result = await self.mcp_client.call_tool(tool_name, args)
        
        # 4. State: VERIFYING
        AgentStateMachine.transition(task, AgentState.VERIFYING)
        
        # 5. Logic: Auto-verify for now
        AgentStateMachine.commit_task(task, result)
        
        self.current_task = None
        return task
