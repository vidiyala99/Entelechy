import pytest
from entelechy.memory.short_term import ShortTermMemory
from entelechy.memory.long_term import LongTermMemory
from entelechy.kernel.interfaces import AgentPlan, TaskNode, AgentState

def test_short_term_persistence():
    memory = ShortTermMemory()
    plan = AgentPlan(goal="Test Persistence", dag=[TaskNode(id="t1", description="task 1")])
    
    memory.set_plan("p1", plan)
    retrieved = memory.get_plan("p1")
    
    assert retrieved is not None
    assert retrieved.goal == "Test Persistence"
    assert retrieved.dag[0].id == "t1"

def test_short_term_state_update():
    memory = ShortTermMemory()
    plan = AgentPlan(goal="Test Update", dag=[TaskNode(id="t1", description="task 1")])
    memory.set_plan("p1", plan)
    
    memory.update_task_state("p1", "t1", AgentState.EXECUTING)
    updated_plan = memory.get_plan("p1")
    assert updated_plan.dag[0].status == AgentState.EXECUTING

def test_long_term_archive_and_search():
    memory = LongTermMemory()
    memory.archive_outcome("Weather in London", {"temp": 20, "condition": "Sunny"})
    memory.archive_outcome("Stock price of Apple", {"price": 180})
    
    results = memory.search("Weather")
    assert len(results) == 1
    assert "London" in results[0]["goal"]
    assert results[0]["outcome"]["temp"] == 20
    
    results_none = memory.search("Mars")
    assert len(results_none) == 0
