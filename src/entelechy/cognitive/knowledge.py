from typing import List, Dict, Any, Optional
from entelechy.config import logger

from entelechy.memory.long_term import LongTermMemory

class KnowledgeInterface:
    """Interface for Semantic RAG and knowledge retrieval."""
    
    def __init__(self, memory: Optional[LongTermMemory] = None):
        self.memory = memory or LongTermMemory()

    async def search_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Searches long-term semantic memory for relevant context."""
        logger.info(f"Searching knowledge for: {query}")
        results = self.memory.search(query)
        
        # Format results for the Reasoner
        formatted_results = []
        for res in results:
            formatted_results.append({
                "id": res.get("timestamp", "unknown"),
                "content": f"Goal: {res.get('goal')} | Result: {res.get('outcome')}",
                "score": res.get("score", 0.9)
            })
        return formatted_results

    def format_results(self, results: List[Dict[str, Any]]) -> str:
        """Formats search results for inclusion in model context."""
        formatted = "KNOWLEDGE_SEARCH_RESULTS:\n"
        for res in results:
            formatted += f"- ({res['score']}) {res['content']}\n"
        return formatted
