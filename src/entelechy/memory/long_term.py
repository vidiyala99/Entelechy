from typing import List, Dict, Any
from entelechy.config import logger
import datetime

class LongTermMemory:
    """Simulates a vector store (e.g., pgvector) for semantic archival of outcomes."""
    
    def __init__(self):
        # In a real system, this would be a vector database
        self._archive: List[Dict[str, Any]] = []
        logger.info("Long-Term Memory (Vector Store Sim) initialized")

    def archive_outcome(self, goal: str, outcome: Any):
        """Archives a completed task/goal outcome for future retrieval."""
        entry = {
            "goal": goal,
            "outcome": outcome,
            "timestamp": datetime.datetime.now().isoformat(),
            "vector": self._mock_embed(goal) # Simulated embedding
        }
        self._archive.append(entry)
        logger.info(f"Outcome archived for goal: {goal}")

    def search(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Simulates semantic search over archived outcomes."""
        logger.info(f"Searching long-term memory for: {query}")
        # Naive keyword match for simulation
        results = [
            e for e in self._archive 
            if query.lower() in e["goal"].lower() or any(query.lower() in str(v).lower() for v in e.values())
        ]
        return results[:limit]

    def _mock_embed(self, text: str) -> List[float]:
        """Simulates a 1536-dim embedding vector."""
        return [0.1] * 10 # Truncated for mock
