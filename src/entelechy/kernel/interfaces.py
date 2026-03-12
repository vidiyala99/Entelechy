from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class AgentState(str, Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    COMMITTED = "committed"
    FAILED = "failed"

class TaskNode(BaseModel):
    id: str
    description: str
    dependencies: List[str] = []
    status: AgentState = AgentState.PENDING
    result: Optional[Any] = None
    assigned_agent: Optional[str] = None

class AgentPlan(BaseModel):
    goal: str
    dag: List[TaskNode] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class KernelInterrupt(BaseModel):
    type: str # e.g., "HITL", "RESOURCE_CONTENTION"
    reason: str
    task_id: str
    data: Dict[str, Any] = {}

class AgentContext(BaseModel):
    history: List[Dict[str, Any]] = []
    current_task_id: Optional[str] = None
    variables: Dict[str, Any] = {}
