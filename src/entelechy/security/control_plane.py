from typing import Any, Dict, Optional
from entelechy.config import logger
from entelechy.security.policy_engine import PolicyEngine

class ControlPlane:
    """Centralized security controller for Entelechy."""
    
    def __init__(self, policy_engine: Optional[PolicyEngine] = None):
        self.policy_engine = policy_engine or PolicyEngine()
        logger.info("Control Plane initialized with Policy Engine")

    def authorize_action(self, agent_id: str, action_type: str, resource_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Validates an action against policies and logs the decision."""
        logger.info(f"Control Plane evaluating: {agent_id} -> {action_type} -> {resource_id}")
        
        is_allowed = self.policy_engine.is_authorized(
            principal=f"Agent::\"{agent_id}\"",
            action=f"Action::\"{action_type}\"",
            resource=f"Resource::\"{resource_id}\"",
            context=context
        )
        
        # Logic for HITL escalation
        if not is_allowed and context and context.get("requires_hitl"):
             logger.info("Action requires Human-in-the-Loop escalation")
             # In a real system, this would trigger a Kernel interrupt
             return False # Blocked until HITL resolved
             
        return is_allowed

    def add_policy(self, principal: str, action: str, resource: str, effect: str = "permit", condition: Optional[str] = None):
        """Dynamic policy management for the Control Plane."""
        if effect == "permit":
            self.policy_engine.permit(principal, action, resource, condition)
        else:
            self.policy_engine.forbid(principal, action, resource)
        logger.info(f"New dynamic policy added: {effect} {principal} {action} {resource}")
