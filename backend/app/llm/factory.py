import os
from functools import lru_cache
from typing import Optional
from .base import AbstractLLMClient
from .bedrock import BedrockClient
from .mistral import MistralClient

class LLMFactory:
    @staticmethod
    def get_client() -> AbstractLLMClient:
        provider = os.getenv("LLM_PROVIDER", "mock").lower()
        
        if provider == "aws":
            return BedrockClient(
                region_name=os.getenv("AWS_REGION", "eu-central-1"),
                model_id=os.getenv("AWS_BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20240620-v1:0")
            )
        elif provider == "mistral":
            return MistralClient(
                api_key=os.getenv("MISTRAL_API_KEY", ""),
                model_id=os.getenv("MISTRAL_MODEL_ID", "mistral-large-latest")
            )
        elif provider == "openai":
            from .openai_client import OpenAIClient
            return OpenAIClient()
        else:
            # Default to Mock
            from .mock import MockLLMClient
            return MockLLMClient()

@lru_cache()
def get_llm_client() -> AbstractLLMClient:
    return LLMFactory.get_client()
