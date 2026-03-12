from typing import Any, Dict, Optional
from entelechy.config import logger

class SandboxError(Exception):
    """Raised when code execution in the sandbox violates policy."""
    pass

class SecureSandbox:
    """Simulates a secure execution environment (e.g., Firecracker MicroVM)."""
    
    def __init__(self, allowed_modules: Optional[list] = None):
        self.allowed_modules = allowed_modules or ["math", "json", "datetime"]
        logger.info(f"Initialized Secure Sandbox with modules: {self.allowed_modules}")

    def run_code(self, code: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulates running untrusted code in an isolated environment."""
        logger.info("Attempting to run code in sandbox (simulated)")
        
        # Security Check: Mocking static analysis
        forbidden_keywords = ["import os", "import subprocess", "open(", "eval("]
        for keyword in forbidden_keywords:
            if keyword in code:
                logger.error(f"Security violation: Code contains {keyword}")
                raise SandboxError(f"Security violation: {keyword} is not allowed in sandbox")
        
        # Execution (Simulated)
        try:
            logger.info("Code passed security check. Executing...")
            # In a real system, this would happen in a Firecracker VM
            # Here we just mock the result
            return {"status": "success", "output": "Simulated execution successful"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
