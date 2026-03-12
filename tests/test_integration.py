import pytest
from entelechy.main import EntelechyAOS
from entelechy.kernel.interfaces import AgentState

@pytest.mark.asyncio
async def test_entelechy_intent_to_outcome_flow():
    aos = EntelechyAOS()
    intent = "Deploy a secure web server"
    
    success = await aos.execute_intent(intent)
    
    # Verify end-to-end success
    assert success is True
    
    # Verify Short-term persistence
    # The last goal used reasoner which defaults to task_1/task_2 ids
    plan = aos.short_term.get_plan("plan_1") # Reasoner default id is plan_1
    assert plan is not None
    assert all(task.status == AgentState.COMMITTED for task in plan.dag)
    
    # Verify Long-term archival
    archive = aos.long_term.search(intent)
    assert len(archive) == 1
    assert "successfully" in archive[0]["outcome"]

@pytest.mark.asyncio
async def test_entelechy_security_denial_flow():
    aos = EntelechyAOS()
    # Mocking a situation where worker is NOT authorized (resetting policies)
    aos.control_plane.policy_engine.forbids = []
    aos.control_plane.policy_engine.permits = []
    
    # Override the execute_intent loop logic for a targeted test or use a special intent
    # Here we just verify that a lack of policy results in failure
    intent = "Unauthorized Action"
    
    # We need to ensure we don't ADD the permit in our main loop for this test
    # So we'll mock the add_policy to be a no-op
    aos.control_plane.add_policy = lambda *args, **kwargs: None
    
    success = await aos.execute_intent(intent)
    assert success is False
