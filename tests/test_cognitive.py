import pytest
from aos.cognitive.reasoner import Reasoner
from aos.cognitive.context import ContextEngineer
from aos.cognitive.knowledge import KnowledgeInterface
from aos.kernel.interfaces import AgentPlan

def test_reasoner_plan_generation():
    reasoner = Reasoner()
    goal = "Build a weather reporting agent"
    plan = reasoner.plan_goal(goal)
    
    assert isinstance(plan, AgentPlan)
    assert plan.goal == goal
    assert len(plan.dag) >= 2
    assert plan.dag[0].id == "task_1"
    assert plan.dag[1].dependencies == ["task_1"]

def test_context_engineer_compilation():
    engineer = ContextEngineer("You are a helpful assistant.")
    engineer.add_event("tool_call", {"tool": "weather", "result": "sunny"})
    
    context = engineer.get_compiled_context()
    assert "STABLE_PREFIX" in context
    assert "weather" in context
    assert "sunny" in context

@pytest.mark.asyncio
async def test_knowledge_interface_search():
    interface = KnowledgeInterface()
    results = await interface.search_knowledge("security policies")
    assert len(results) > 0
    assert results[0]["score"] > 0.9
    
    formatted = interface.format_results(results)
    assert "KNOWLEDGE_SEARCH_RESULTS" in formatted
