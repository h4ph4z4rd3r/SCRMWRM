import asyncio
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.llm.factory import get_llm_client
from app.llm.base import LLMMessage

async def main():
    print("--- LLM Verification Script ---")
    provider = os.getenv("LLM_PROVIDER", "aws")
    print(f"Testing Provider: {provider}")
    
    try:
        client = get_llm_client()
        print(f"Client initialized: {client.__class__.__name__}")
        
        messages = [
            LLMMessage(role="user", content="Hello! Are you hosted in the EU? Reply with 'Yes' and your location.")
        ]
        
        print("\nSending prompt...")
        response = await client.generate_response(messages)
        print(f"\nResponse:\n{response}")
        print("\nTest Passed! ✅")
        
    except Exception as e:
        print(f"\nTest Failed! ❌\nError: {e}")

if __name__ == "__main__":
    asyncio.run(main())
