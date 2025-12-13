from typing import TypedDict, List, Optional, Annotated
import operator
from uuid import UUID
from app.llm import LLMMessage

class NegotiationState(TypedDict):
    contract_id: str # UUID string
    supplier_id: str # UUID string
    current_clause_text: str
    
    # Context (Populated by Agents)
    # We store these as dicts (dumped models) to be serializable
    policy_analysis: Optional[dict] 
    risk_profile: Optional[dict]
    
    # Chat History
    messages: Annotated[List[LLMMessage], operator.add]
    
    # Decisions
    strategy_decision: Optional[str] # "ACCEPT", "REJECT", "COUNTER", "NEEDS_HUMAN"
    proposed_redline: Optional[str]
    reasoning: Optional[str]
    
    # HITL Control
    agency_level: str # STRICT, MEDIUM, AUTONOMOUS
    human_approval_status: Optional[str] # PENDING_STRATEGY, PENDING_DRAFT, APPROVED, REJECTED
    human_feedback: Optional[str]
