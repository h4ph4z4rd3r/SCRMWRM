from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: str
    content: str

class AbstractLLMClient(ABC):
    @abstractmethod
    async def generate_response(
        self, 
        messages: List[LLMMessage], 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a text response from the LLM.
        """
        pass

    @abstractmethod
    async def generate_json(
        self, 
        messages: List[LLMMessage], 
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured JSON response enforcing the given schema.
        """
        pass

    @abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate a vector embedding for the given text.
        """
        pass
