import asyncio
from typing import List, Dict, Any, Optional
from .base import AbstractLLMClient, LLMMessage

class MockLLMClient(AbstractLLMClient):
    async def generate_response(
        self, 
        messages: List[LLMMessage], 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        # Simulate latency
        await asyncio.sleep(1.0)
        return "This is a mock response from the AI Agent. Please configure a real LLM Provider for dynamic content."

    async def generate_json(
        self, 
        messages: List[LLMMessage], 
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        await asyncio.sleep(1.0)
        # Return a safe default matching the negotiation schema
        return {
            "decision": "COUNTER",
            "reasoning": "This is a mock analysis. The clause was flagged for review requiring a counter-proposal."
        }

    async def generate_embedding(self, text: str) -> List[float]:
        # Return random or zero vector of length 1536
        return [0.0] * 1536
