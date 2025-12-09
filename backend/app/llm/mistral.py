import json
import logging
import os
from typing import List, Dict, Any, Optional
from mistralai import Mistral
from .base import AbstractLLMClient, LLMMessage

logger = logging.getLogger(__name__)

class MistralClient(AbstractLLMClient):
    def __init__(self, api_key: str, model_id: str = "mistral-large-latest"):
        self.client = Mistral(api_key=api_key)
        self.model_id = model_id

    async def generate_response(
        self, 
        messages: List[LLMMessage], 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        
        chat_messages = []
        if system_prompt:
             chat_messages.append({"role": "system", "content": system_prompt})
             
        for m in messages:
            chat_messages.append({"role": m.role, "content": m.content})

        try:
            chat_response = self.client.chat.complete(
                model=self.model_id,
                messages=chat_messages,
                temperature=temperature,
            )
            
            return chat_response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error invoking Mistral model {self.model_id}: {e}")
            raise

    async def generate_json(
        self, 
        messages: List[LLMMessage], 
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # Mistral supports 'json_mode' in newer models
        json_instruction = f"\nYou must respond with valid JSON adhering to this schema:\n{json.dumps(schema, indent=2)}"
        full_system_prompt = (system_prompt or "") + json_instruction
        
        chat_messages = []
        if full_system_prompt:
             chat_messages.append({"role": "system", "content": full_system_prompt})
             
        for m in messages:
            chat_messages.append({"role": m.role, "content": m.content})

        try:
            chat_response = self.client.chat.complete(
                model=self.model_id,
                messages=chat_messages,
                temperature=0.1,
                response_format={"type": "json_object"} 
            )
            
            return json.loads(chat_response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error generating JSON with Mistral: {e}")
            raise

    async def generate_embedding(self, text: str) -> List[float]:
        try:
            resp = self.client.embeddings.create(
                model="mistral-embed",
                inputs=[text]
            )
            return resp.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding with Mistral: {e}")
            raise
