from typing import Any
from aos.config import logger
from aos.kernel.interfaces import AgentState, TaskNode

class StateMachineError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass

class AgentStateMachine:
    """Manages the state transitions for an agent task."""
    
    VALID_TRANSITIONS = {
        AgentState.PENDING: [AgentState.PLANNING, AgentState.FAILED],
        AgentState.PLANNING: [AgentState.EXECUTING, AgentState.FAILED],
        AgentState.EXECUTING: [AgentState.VERIFYING, AgentState.FAILED],
        AgentState.VERIFYING: [AgentState.COMMITTED, AgentState.FAILED, AgentState.EXECUTING], # Can go back to executing if verification fails
        AgentState.COMMITTED: [],
        AgentState.FAILED: [AgentState.PENDING] # Can be retried
    }

    @staticmethod
    def transition(task: TaskNode, next_state: AgentState):
        """Transitions a task to a new state if valid."""
        current_state = task.status
        
        if next_state not in AgentStateMachine.VALID_TRANSITIONS.get(current_state, []):
            error_msg = f"Invalid transition from {current_state} to {next_state}"
            logger.error(error_msg)
            raise StateMachineError(error_msg)
            
        logger.info(f"Task {task.id} transitioning: {current_state} -> {next_state}")
        task.status = next_state
        
        return task

    @staticmethod
    def claim_task(task: TaskNode, agent_id: str):
        """Assigns an agent to a task and moves it to EXECUTING if it was in PLANNING."""
        if task.status != AgentState.PLANNING:
            raise StateMachineError(f"Task {task.id} must be in PLANNING to be claimed, current: {task.status}")
        
        task.assigned_agent = agent_id
        return AgentStateMachine.transition(task, AgentState.EXECUTING)

    @staticmethod
    def fail_task(task: TaskNode, reason: str):
        """Moves a task to FAILED state."""
        logger.warning(f"Task {task.id} failed: {reason}")
        task.result = {"error": reason}
        return AgentStateMachine.transition(task, AgentState.FAILED)

    @staticmethod
    def commit_task(task: TaskNode, result: Any):
        """Moves a task to COMMITTED state with result."""
        if task.status != AgentState.VERIFYING:
             raise StateMachineError(f"Task {task.id} must be in VERIFYING to be committed, current: {task.status}")
             
        task.result = result
        return AgentStateMachine.transition(task, AgentState.COMMITTED)
