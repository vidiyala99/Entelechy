from typing import Optional, Callable
from entelechy.kernel.interfaces import KernelInterrupt
from entelechy.config import logger, settings

class InterruptHandler:
    """Handles system interrupts, HITL gates, and resource contention."""
    
    def __init__(self, hitl_callback: Optional[Callable[[KernelInterrupt], bool]] = None):
        self.hitl_callback = hitl_callback

    def trigger_interrupt(self, interrupt: KernelInterrupt) -> bool:
        """Processes an interrupt and returns True if resolved, False otherwise."""
        logger.warning(f"Interrupt triggered: {interrupt.type} for task {interrupt.task_id} - Reason: {interrupt.reason}")
        
        if interrupt.type == "HITL":
             if self.hitl_callback:
                 return self.hitl_callback(interrupt)
             else:
                 logger.error("HITL interrupt triggered but no callback registered")
                 return False # Blocked
                 
        elif interrupt.type == "RESOURCE_CONTENTION":
            # Logic to resolve contention would go here
            logger.info(f"Resolving resource contention: {interrupt.data}")
            return True
            
        return False

    def check_confidence(self, task_id: str, score: float) -> bool:
        """Checks if confidence score is below threshold and triggers HITL if needed."""
        if score < settings.HITL_CONFIDENCE_THRESHOLD:
            interrupt = KernelInterrupt(
                type="HITL",
                reason=f"Confidence score {score} below threshold {settings.HITL_CONFIDENCE_THRESHOLD}",
                task_id=task_id,
                data={"score": score}
            )
            return self.trigger_interrupt(interrupt)
        return True
