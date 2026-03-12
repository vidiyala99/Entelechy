from entelechy.kernel.interfaces import TaskNode, AgentState
from entelechy.kernel.state_machine import AgentStateMachine
from entelechy.execution.mcp_client import MCPClient
from typing import Optional
from entelechy.security.control_plane import ControlPlane
from entelechy.config import logger

class Worker:
    """Represents a worker agent that performs physical work via tools."""
    
    def __init__(self, worker_id: str, mcp_client: MCPClient, control_plane: Optional[ControlPlane] = None):
        self.worker_id = worker_id
        self.mcp_client = mcp_client
        self.control_plane = control_plane or ControlPlane()
        self.current_task: Optional[TaskNode] = None

    async def process_task(self, task: TaskNode) -> TaskNode:
        """Processes a task assigned by the Kernel."""
        self.current_task = task
        logger.info(f"Worker {self.worker_id} processing task {task.id}: {task.description}")
        
        # 1. State: CLAIMED (handled by Kernel, but worker acknowledges)
        AgentStateMachine.transition(task, AgentState.EXECUTING)
        
        # 2. Logic: Mocking tool selection based on description
        tool_name = "google_search" if "search" in task.description.lower() else "read_file"
        args = {"query": task.description} if tool_name == "google_search" else {"path": "data.txt"}
        
        # 3. Security: Authorize the tool call
        if not self.control_plane.authorize_action(self.worker_id, tool_name, args.get("path", "web")):
             error_msg = f"Security Violation: Action '{tool_name}' unauthorized for worker {self.worker_id}"
             logger.error(error_msg)
             AgentStateMachine.fail_task(task, error_msg)
             self.current_task = None
             return task

        # 4. Execution
        result = await self.mcp_client.call_tool(tool_name, args)
        
        # 4. State: VERIFYING
        AgentStateMachine.transition(task, AgentState.VERIFYING)
        
        # 5. Logic: Auto-verify for now
        AgentStateMachine.commit_task(task, result)
        
        self.current_task = None
        return task
