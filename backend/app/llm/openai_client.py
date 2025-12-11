from typing import List, Dict, Any, Optional
import json
import logging
import os
from openai import AsyncOpenAI
from app.llm.base import AbstractLLMClient, LLMMessage
from app.core.config import settings

logger = logging.getLogger(__name__)

class OpenAIClient(AbstractLLMClient):
    """
    Client for OpenAI API (GPT-4o, etc.)
    """
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4o" # or gpt-3.5-turbo if cost is concern

    async def generate_response(self, messages: List[LLMMessage], system_prompt: Optional[str] = None) -> str:
        """
        Generates a text response from OpenAI.
        """
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
            
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=0.7
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            raise

    async def generate_json(self, messages: List[LLMMessage], schema: Dict[str, Any], system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Generates a JSON response using 'response_format'.
        """
        formatted_messages = []
        if system_prompt:
            formatted_messages.append({"role": "system", "content": system_prompt})
            
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
            
        # Append schema instruction if not implicit, though 'json_object' usually just enforces JSON.
        # It's good practice to remind the model of the schema in the system prompt or user prompt.
        # We'll assume the caller handled the schema description in the prompts, 
        # but we can enforce valid JSON parsing here.
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=formatted_messages,
                temperature=0.2, # Lower temp for structured data
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"OpenAI JSON Error: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        try:
            response = await self.client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI Embedding Error: {e}")
            raise
