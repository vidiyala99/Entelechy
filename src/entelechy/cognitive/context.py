from typing import List, Dict, Any
from entelechy.config import logger
import json

class ContextEngineer:
    """Manages high-density context for agents using Prefix/Suffix engineering."""
    
    def __init__(self, system_instruction: str):
        self.stable_prefix = system_instruction
        self.variable_suffix: List[Dict[str, Any]] = []
        self.max_suffix_items = 5

    def add_event(self, event_type: str, data: Any):
        """Adds a new event (tool output, decision) to the variable suffix."""
        self.variable_suffix.append({
            "type": event_type,
            "data": data,
            "timestamp": "2026-03-11" # Simplified for mock
        })
        
        # Keep only the latest N items
        if len(self.variable_suffix) > self.max_suffix_items:
            self.variable_suffix = self.variable_suffix[-self.max_suffix_items:]

    def get_compiled_context(self) -> str:
        """Compiles the prefix and suffix into a single context string."""
        context = f"STABLE_PREFIX:\n{self.stable_prefix}\n\n"
        context += "VARIABLE_SUFFIX (Latest Events):\n"
        
        for item in self.variable_suffix:
            context += f"- [{item['type']}]: {json.dumps(item['data'])}\n"
            
        return context

    def compact_context(self) -> str:
        """Summarizes past context to reduce token waste."""
        # Simple mock compaction
        summary = f"Summary of {len(self.variable_suffix)} past events."
        logger.info("Compacting context")
        return summary
