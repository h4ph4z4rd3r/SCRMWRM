import json
import boto3
import logging
from typing import List, Dict, Any, Optional
from .base import AbstractLLMClient, LLMMessage

logger = logging.getLogger(__name__)

class BedrockClient(AbstractLLMClient):
    def __init__(self, region_name: str, model_id: str):
        self.client = boto3.client(service_name="bedrock-runtime", region_name=region_name)
        self.model_id = model_id

    async def generate_response(
        self, 
        messages: List[LLMMessage], 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        
        # Convert to Anthropic format
        anthropic_messages = [
            {"role": m.role, "content": m.content} for m in messages
        ]
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4096,
            "messages": anthropic_messages,
            "temperature": temperature,
        }
        
        if system_prompt:
            body["system"] = system_prompt

        try:
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(body)
            )
            
            response_body = json.loads(response.get("body").read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            logger.error(f"Error invoking Bedrock model {self.model_id}: {e}")
            raise

    async def generate_json(
        self, 
        messages: List[LLMMessage], 
        schema: Dict[str, Any],
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        
        # Enhance system prompt with JSON instruction
        json_instruction = f"\nYou must respond with valid JSON adhering to this schema:\n{json.dumps(schema, indent=2)}\nResponse must be ONLY JSON."
        full_system_prompt = (system_prompt or "") + json_instruction
        
        text_response = await self.generate_response(messages, full_system_prompt, temperature=0.1)
        
        try:
            # Basic cleanup if model includes markdown code blocks
            clean_text = text_response.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.startswith("```"):
                clean_text = clean_text[3:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
                
            return json.loads(clean_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from Bedrock response: {text_response}")
            raise ValueError("LLM failed to generate valid JSON")

    async def generate_embedding(self, text: str) -> List[float]:
        # Using Titan Embeddings v1 by default for embeddings
        embedding_model_id = "amazon.titan-embed-text-v1"
        
        body = json.dumps({
            "inputText": text
        })
        
        try:
            response = self.client.invoke_model(
                modelId=embedding_model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            
            response_body = json.loads(response.get("body").read())
            return response_body.get("embedding")
            
        except Exception as e:
            logger.error(f"Error generating embedding with Bedrock ({embedding_model_id}): {e}")
            raise
