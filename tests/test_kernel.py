import pytest
from entelechy.kernel.interfaces import TaskNode, AgentState, AgentPlan
from entelechy.kernel.state_machine import AgentStateMachine, StateMachineError
from entelechy.kernel.scheduler import Scheduler
from entelechy.kernel.interrupts import InterruptHandler, KernelInterrupt

def test_state_machine_valid_transitions():
    task = TaskNode(id="test1", description="test task")
    assert task.status == AgentState.PENDING
    
    AgentStateMachine.transition(task, AgentState.PLANNING)
    assert task.status == AgentState.PLANNING
    
    AgentStateMachine.claim_task(task, "agent1")
    assert task.status == AgentState.EXECUTING
    assert task.assigned_agent == "agent1"
    
    AgentStateMachine.transition(task, AgentState.VERIFYING)
    assert task.status == AgentState.VERIFYING
    
    AgentStateMachine.commit_task(task, {"output": "success"})
    assert task.status == AgentState.COMMITTED
    assert task.result == {"output": "success"}

def test_state_machine_invalid_transition():
    task = TaskNode(id="test2", description="test task")
    with pytest.raises(StateMachineError):
        AgentStateMachine.transition(task, AgentState.COMMITTED)

def test_scheduler_dag_execution():
    scheduler = Scheduler()
    node1 = TaskNode(id="n1", description="node 1")
    node2 = TaskNode(id="n2", description="node 2", dependencies=["n1"])
    plan = AgentPlan(goal="test goal", dag=[node1, node2])
    
    plan_id = scheduler.add_plan(plan)
    
    # Ready tasks should only be n1
    ready = scheduler.get_ready_tasks(plan_id)
    assert len(ready) == 1
    assert ready[0].id == "n1"
    
    # Move n1 to planning/executing/verifying/committed
    scheduler.update_task_status(plan_id, "n1", AgentState.PLANNING)
    scheduler.update_task_status(plan_id, "n1", AgentState.EXECUTING)
    scheduler.update_task_status(plan_id, "n1", AgentState.VERIFYING)
    scheduler.update_task_status(plan_id, "n1", AgentState.COMMITTED, {"res": 1})
    
    # Now n2 should be ready
    ready = scheduler.get_ready_tasks(plan_id)
    assert len(ready) == 1
    assert ready[0].id == "n2"
    
    assert not scheduler.is_plan_complete(plan_id)
    scheduler.update_task_status(plan_id, "n2", AgentState.PLANNING)
    scheduler.update_task_status(plan_id, "n2", AgentState.EXECUTING)
    scheduler.update_task_status(plan_id, "n2", AgentState.VERIFYING)
    scheduler.update_task_status(plan_id, "n2", AgentState.COMMITTED, {"res": 2})
    assert scheduler.is_plan_complete(plan_id)

def test_interrupt_handler():
    def mock_hitl(interrupt):
        return True # User approves
        
    handler = InterruptHandler(hitl_callback=mock_hitl)
    
    # Test confidence check
    assert handler.check_confidence("t1", 0.9) is True
    assert handler.check_confidence("t1", 0.5) is True # Approved by mock_hitl
    
    # Test resource contention
    interrupt = KernelInterrupt(type="RESOURCE_CONTENTION", reason="lock", task_id="t2")
    assert handler.trigger_interrupt(interrupt) is True
