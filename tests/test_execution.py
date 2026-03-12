import pytest
from aos.execution.mcp_client import MCPClient
from aos.execution.worker import Worker
from aos.kernel.state_machine import AgentStateMachine
from aos.execution.sandbox import SecureSandbox, SandboxError
from aos.kernel.interfaces import TaskNode, AgentState

@pytest.mark.asyncio
async def test_mcp_client_tool_call():
    client = MCPClient("http://mock-mcp-server")
    result = await client.call_tool("google_search", {"query": "AOS 2026"})
    
    assert result["status"] == "success"
    assert "AOS 2026" in result["results"][0]

@pytest.mark.asyncio
async def test_worker_processing():
    client = MCPClient("http://mock-mcp-server")
    worker = Worker("worker_1", client)
    task = TaskNode(id="t_exec_1", description="Search for agentic os")
    AgentStateMachine.transition(task, AgentState.PLANNING)
    
    processed_task = await worker.process_task(task)
    
    assert processed_task.status == AgentState.COMMITTED
    assert "results" in processed_task.result

def test_sandbox_security():
    sandbox = SecureSandbox()
    
    # Safe code
    result = sandbox.run_code("x = 10 + 20", {})
    assert result["status"] == "success"
    
    # Unsafe code
    with pytest.raises(SandboxError):
        sandbox.run_code("import os; os.remove('system.db')", {})
