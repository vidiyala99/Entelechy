from typing import List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from entelechy.kernel.interfaces import AgentPlan, TaskNode
from entelechy.config import logger

class ReasonerState(TypedDict):
    goal: str
    plan: Optional[AgentPlan]
    intermediate_steps: List[str]
    status: str

class Reasoner:
    """The brain of the Entelechy, responsible for planning and goal decomposition."""
    
    def __init__(self):
        self.workflow = self._build_graph()

    def _build_graph(self):
        """Constructs the LangGraph workflow for reasoning."""
        graph = StateGraph(ReasonerState)
        
        # Define nodes
        graph.add_node("analyze_goal", self._analyze_goal)
        graph.add_node("generate_dag", self._generate_dag)
        
        # Define edges
        graph.set_entry_point("analyze_goal")
        graph.add_edge("analyze_goal", "generate_dag")
        graph.add_edge("generate_dag", END)
        
        return graph.compile()

    def _analyze_goal(self, state: ReasonerState) -> ReasonerState:
        """Analyzes the initial goal and breaks it down into high-level steps."""
        logger.info(f"Analyzing goal: {state['goal']}")
        # In a real 2026 system, this would call an LLM
        # Mocking the analysis for now
        state['intermediate_steps'] = [f"Step for: {state['goal']}"]
        return state

    def _generate_dag(self, state: ReasonerState) -> ReasonerState:
        """Generates a Directed Acyclic Graph (DAG) of TaskNodes."""
        logger.info("Generating task DAG")
        # In a real system, the LLM would output the JSON structure of the DAG
        # Mocking a simple sequential DAG for now
        node1 = TaskNode(id="task_1", description=f"Initial task for {state['goal']}")
        node2 = TaskNode(id="task_2", description=f"Finalize results for {state['goal']}", dependencies=["task_1"])
        
        state['plan'] = AgentPlan(goal=state['goal'], dag=[node1, node2])
        state['status'] = "planned"
        return state

    def plan_goal(self, goal: str) -> AgentPlan:
        """Executes the reasoning workflow to create a plan for a goal."""
        initial_state = {
            "goal": goal,
            "plan": None,
            "intermediate_steps": [],
            "status": "started"
        }
        final_state = self.workflow.invoke(initial_state)
        return final_state['plan']
