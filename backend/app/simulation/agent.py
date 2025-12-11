from typing import List, Dict, Any
import os
from app.simulation.persona import SupplierPersona
from app.llm import get_llm_client, LLMMessage

class SupplierAgent:
    """
    Simulates the counter-party in a negotiation.
    """
    def __init__(self, persona_id: str):
        self.persona = self._load_persona(persona_id)
        self.llm = get_llm_client()

    def _load_persona(self, persona_id: str) -> SupplierPersona:
        # Assuming run from backend/ dir or similar, adjusting path logic
        # For simplicity, hardcode relative to this file or use env var
        base_path = os.path.join(os.path.dirname(__file__), "../../data/suppliers")
        path = os.path.join(base_path, f"{persona_id}.yaml")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Persona {persona_id} not found at {path}")
        return SupplierPersona.load_from_yaml(path)

    def _build_system_prompt(self) -> str:
        return f"""You are {self.persona.name}, a supplier representing a company.
Your negotiation style is: {self.persona.style}.
Your tone is: {self.persona.negotiation_tone}.

Your Goals:
{chr(10).join([f"- {g}" for g in self.persona.goals])}

Your Constraints (Non-negotiable):
{chr(10).join([f"- {c}" for c in self.persona.constraints])}

Instructions:
1. Read the latest proposal from the buyer.
2. If it meets your goals, accept it.
3. If it violates constraints, reject it firmly.
4. Otherwise, counter-propose to move closer to your goals.
5. Keep responses concise (under 100 words) and purely conversational (do not output internal thought process unless asked).
"""

    async def generate_reply(self, conversation_history: List[Dict[str, str]], latest_proposal: str) -> str:
        """
        Generates the next response in the conversation.
        """
        messages = [
            LLMMessage(role="system", content=self._build_system_prompt())
        ]
        
        # Add history
        for msg in conversation_history:
            role = "assistant" if msg['sender'] == 'supplier' else "user"
            messages.append(LLMMessage(role=role, content=msg['content']))
            
        messages.append(LLMMessage(role="user", content=f"Latest Proposal/Message: {latest_proposal}"))
        
        response = await self.llm.generate_response(messages)
        return response
