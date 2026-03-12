from typing import List, Dict, Any, Optional
from entelechy.config import logger
import re

class PolicyEngine:
    """Evaluates security policies using 2026 Cedar-inspired logic."""
    
    def __init__(self):
        # Default policy: deny all, permit specific
        self.permits = []
        self.forbids = []
        self._load_default_policies()

    def _load_default_policies(self):
        """Loads basic safety policies."""
        self.permit("Agent::\"*\"", "Action::\"Read\"", "Resource::\"*\"")
        self.forbid("Agent::\"*\"", "Action::\"Delete\"", "Resource::\"SystemFiles\"")

    def permit(self, principal: str, action: str, resource: str, condition: Optional[str] = None):
        self.permits.append({"principal": principal, "action": action, "resource": resource, "condition": condition})

    def forbid(self, principal: str, action: str, resource: str):
        self.forbids.append({"principal": principal, "action": action, "resource": resource})

    def is_authorized(self, principal: str, action: str, resource: str, context: Dict[str, Any] = None) -> bool:
        """Evaluates if an action is authorized."""
        # 1. Check Forbids (Forbid overrides Permit)
        for policy in self.forbids:
            if self._match(policy, principal, action, resource):
                logger.warning(f"Access FORBIDDEN by policy: {policy} for {principal}")
                return False
        
        # 2. Check Permits
        for policy in self.permits:
            if self._match(policy, principal, action, resource):
                # Check condition if exists
                if policy.get("condition"):
                    if not self._eval_condition(policy["condition"], context):
                        continue
                logger.info(f"Access PERMITTED by policy: {policy} for {principal}")
                return True
                
        logger.warning(f"Access DENIED (No permit found) for {principal} on {resource}")
        return False

    def _match(self, policy: Dict[str, str], principal: str, action: str, resource: str) -> bool:
        """Naive pattern matching for principals, actions, and resources."""
        def pattern_match(p, val):
            if p == "*" or p == val or (p.startswith("\"*\"") and p.endswith("\"*\"")):
                 return True
            # Simple wildcard support Agent::"*"
            clean_p = p.replace("*", ".*").replace("\"", "")
            clean_val = val.replace("\"", "")
            return re.match(f"^{clean_p}$", clean_val) is not None

        return (pattern_match(policy["principal"], principal) and 
                pattern_match(policy["action"], action) and 
                pattern_match(policy["resource"], resource))

    def _eval_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """Simulates condition evaluation (e.g., amount < 500)."""
        if not context: return False
        try:
            # Simple mock evaluation for demo purposes
            if "amount < 500" in condition:
                return context.get("amount", 0) < 500
            return True
        except Exception:
            return False
