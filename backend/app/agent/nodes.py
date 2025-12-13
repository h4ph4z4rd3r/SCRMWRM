from typing import Dict, Any
from uuid import UUID
from datetime import datetime, timezone
import json

from app.agent.state import NegotiationState
from app.llm import get_llm_client, LLMMessage
from app.policy.engine import PolicyEvaluator
from app.supplier.intelligence import SupplierIntelligenceService
from app.database import get_session
from app.models import Supplier, Policy

# Initialize services
# In a real app we might want dependency injection, but for the graph nodes
# we often treat them as functional units.
policy_evaluator = PolicyEvaluator()
supplier_service = SupplierIntelligenceService()
llm = get_llm_client()

async def policy_analysis_node(state: NegotiationState) -> Dict[str, Any]:
    """
    The Lawyer: Checks the current clause text against policies.
    """
    print("--- Node: Policy Analysis ---")
    
    # We need a DB session. We'll grab a fresh one for this operation.
    # Note: In a production graph, we might pass session via 'config'.
    async for session in get_session():
        # TODO: Retrieve the relevant policy based on contract/clause context
        # For now, we fetch a "Standard" policy or the first active one.
        # This is a simplification. In reality, we'd use RAG to find the policy.
        from sqlmodel import select
        result = await session.execute(select(Policy).limit(1))
        policy = result.scalars().first()
        
        if not policy:
            return {"policy_analysis": {"status": "SKIPPED", "reasoning": "No active policy found"}}

        result = await policy_evaluator.evaluate(state["current_clause_text"], policy)
        # Convert Pydantic model to dict for state storage
        return {"policy_analysis": result.dict()}

async def risk_analysis_node(state: NegotiationState) -> Dict[str, Any]:
    """
    The Analyst: Checks supplier risk.
    """
    print("--- Node: Risk Analysis ---")
    supplier_id = UUID(state["supplier_id"])
    
    async for session in get_session():
        # Update/Get risk profile
        profile = await supplier_service.update_supplier_risk_profile(session, supplier_id)
        # Convert SQLModel to dict
        return {"risk_profile": profile.dict()}

async def strategy_node(state: NegotiationState) -> Dict[str, Any]:
    """
    The Negotiator: Decides on the strategy (Accept/Reject/Counter).
    """
    print("--- Node: Strategy Synthesis ---")
    
    # Context
    policy_result = state.get("policy_analysis", {})
    risk_profile = state.get("risk_profile", {})
    clause = state["current_clause_text"]
    
    system_prompt = (
        "You are the Chief Negotiator. Your goal is to decide whether to ACCEPT, REJECT, or COUNTER "
        "a contract clause based on Policy Compliance and Supplier Risk.\n"
        "RULES:\n"
        "1. If Policy Status is NON_COMPLIANT, you MUST REJECT or COUNTER.\n"
        "2. If Risk is HIGH (Score > 70), be more aggressive/protective.\n"
        "3. Output JSON: { \"decision\": \"...\", \"reasoning\": \"...\" }\n"
        "Valid Decisions: ACCEPT, REJECT, COUNTER"
    )
    
    user_content = (
        f"CLAUSE: {clause}\n"
        f"POLICY REPORT: {json.dumps(policy_result, default=str)}\n"
        f"SUPPLIER RISK: {json.dumps(risk_profile, default=str)}\n"
    )
    
    messages = [LLMMessage(role="user", content=user_content)]
    
    schema = {
        "type": "object",
        "properties": {
            "decision": {"type": "string", "enum": ["ACCEPT", "REJECT", "COUNTER"]},
            "reasoning": {"type": "string"}
        },
        "required": ["decision", "reasoning"]
    }
    
    response = await llm.generate_json(messages, schema, system_prompt=system_prompt)
    
    # Update State
    return {
        "strategy_decision": response["decision"],
        "reasoning": response["reasoning"]
    }

async def drafting_node(state: NegotiationState) -> Dict[str, Any]:
    """
    The Scribe: Drafts the counter-proposal if needed.
    """
    print("--- Node: Drafting ---")
    
    if state.get("human_approval_status") == "REJECTED":
        return {
            "proposed_redline": None,
            "messages": [LLMMessage(role="agent", content="Process halted: Strategy rejected by user.")]
        }

    decision = state.get("strategy_decision")
    if decision not in ["COUNTER", "REJECT"]:
        return {
            "proposed_redline": None,
            "messages": [LLMMessage(role="agent", content=f"Result: {decision}\nReasoning: {state.get('reasoning')}")]
        }
        
    clause = state["current_clause_text"]
    reasoning = state["reasoning"]
    
    system_prompt = "You are an expert Legal Drafter. Rewrite the clause to address the issues."
    user_content = f"ORIGINAL: {clause}\nISSUE: {reasoning}\nTASK: Write the new legal text."
    
    messages = [LLMMessage(role="user", content=user_content)]
    # Just text generation here
    new_text = await llm.generate_response(messages, system_prompt=system_prompt)
    
    return {
        "proposed_redline": new_text,
        "messages": [LLMMessage(role="agent", content=f"Proposed Redline ({decision}):\n{new_text}\n\nReasoning: {reasoning}")]
    }

from langgraph.types import Command, interrupt
from app.core.config import settings

async def human_review_gatekeeper(state: NegotiationState) -> Dict[str, Any]:
    """
    Acts as a checkpoint for Human-in-the-Loop.
    Determines if we need to pause based on AGENCY_LEVEL.
    """
    print("--- Node: Human Gatekeeper ---")
    
    level = state.get("agency_level", settings.AGENCY_LEVEL)
    status = state.get("human_approval_status", "")
    
    # Check if we already have approval (resume scenario)
    if status == "APPROVED":
        print("Human Approved. Proceeding.")
        return {"human_approval_status": "PROCESSED"} # Reset or move on
    
    if status == "REJECTED":
        # logic to loop back? For now, we just stop or needs a routing decision
        print("Human Rejected.")
        return {}

    # Logic to trigger interrupt
    needs_review = False
    
    # 1. Strict Mode: Review everything
    if level == "STRICT":
        needs_review = True
        
    # 2. Medium Mode: Review after Strategy (Decision made) but before Drafting? 
    # Or specifically after Drafting to approve the text.
    # Let's say we put this node AFTER Strategy but BEFORE Scribe.
    if level == "MEDIUM":
        needs_review = True
        
    # 3. Autonomous: Review only if explicit request
    if level == "AUTONOMOUS":
        # Check supplier message intent (mocked for now)
        # if "human" in last_message...
        needs_review = False # Default

    if needs_review:
        print(f"[{level}] Pausing for Human Review...")
        # Interrupt!
        # The value returned by interrupt() is provided when confirming/resuming
        human_input = interrupt({"type": "approval_required", "current_context": state.get("reasoning")})
        
        # When resumed...
        return {
            "human_approval_status": human_input.get("status"), # APPROVED / REJECTED
            "human_feedback": human_input.get("feedback")
        }
    
    return {"human_approval_status": "AUTO_APPROVED"}
