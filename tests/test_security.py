import pytest
from entelechy.security.policy_engine import PolicyEngine
from entelechy.security.control_plane import ControlPlane

def test_policy_engine_basic_auth():
    engine = PolicyEngine()
    
    # Test default permit (Read All)
    assert engine.is_authorized("Agent::\"Worker1\"", "Action::\"Read\"", "Resource::\"Data\"") is True
    
    # Test default forbid (Delete SystemFiles)
    assert engine.is_authorized("Agent::\"Worker1\"", "Action::\"Delete\"", "Resource::\"SystemFiles\"") is False

def test_policy_engine_wildcards():
    engine = PolicyEngine()
    engine.permit("Agent::\"Finance*\"", "Action::\"Update\"", "Resource::\"Invoices\"")
    
    assert engine.is_authorized("Agent::\"FinanceBot\"", "Action::\"Update\"", "Resource::\"Invoices\"") is True
    assert engine.is_authorized("Agent::\"GeneralBot\"", "Action::\"Update\"", "Resource::\"Invoices\"") is False

def test_policy_engine_conditions():
    engine = PolicyEngine()
    engine.permit("Agent::\"FinanceBot\"", "Action::\"Pay\"", "Resource::\"Vendor\"", condition="resource.amount < 500")
    
    assert engine.is_authorized("Agent::\"FinanceBot\"", "Action::\"Pay\"", "Resource::\"Vendor\"", {"amount": 200}) is True
    assert engine.is_authorized("Agent::\"FinanceBot\"", "Action::\"Pay\"", "Resource::\"Vendor\"", {"amount": 600}) is False

def test_control_plane_authorization():
    control = ControlPlane()
    control.add_policy("Agent::\"CFO\"", "Action::\"*\"", "Resource::\"*\"", effect="permit")
    
    assert control.authorize_action("CFO", "AnyAction", "AnyResource") is True
    assert control.authorize_action("Intern", "Delete", "Database") is False
