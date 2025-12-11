from typing import Dict, Any, List
from uuid import UUID
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agent.graph import negotiation_graph
from app.agent.state import NegotiationState

router = APIRouter(prefix="/agent", tags=["agent"])

class NegotiationRequest(BaseModel):
    contract_id: str
    supplier_id: str
    clause_text: str
    thread_id: str = "default_thread" # Identifier for the conversation history

@router.post("/negotiate")
async def start_negotiation(request: NegotiationRequest) -> Dict[str, Any]:
    """
    Triggers or resumes the Agentic Negotiation Workflow.
    """
    # Config for persistence
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Initialize State
    initial_state: NegotiationState = {
        "contract_id": request.contract_id,
        "supplier_id": request.supplier_id,
        "current_clause_text": request.clause_text,
        "messages": [],
        "policy_analysis": None,
        "risk_profile": None,
        "strategy_decision": None,
        "proposed_redline": None,
        "reasoning": None,
        "agency_level": "MEDIUM", # Default
        "human_approval_status": "PENDING"
    }
    
    try:
        # Run the Graph with persistence
        # ainvoke will run until it finishes OR hits an interrupt
        final_state = await negotiation_graph.ainvoke(initial_state, config=config)
        
        return {
            "status": "completed",
            "strategy": final_state.get("strategy_decision"),
            "reasoning": final_state.get("reasoning"),
            "redline": final_state.get("proposed_redline")
        }
    except Exception as e:
        # Check if it was an interrupt (not strictly an exception in recent versions, but control flow stops)
        # LangGraph usually returns the state at interrupt.
        # But if we want to catch the interrupt explicitly, we check the snapshot.
        snapshot = negotiation_graph.get_state(config)
        if snapshot.next:
            return {
                "status": "paused",
                "message": "Human approval required.",
                "next_step": snapshot.next,
                "current_reasoning": snapshot.values.get("reasoning")
            }
        
        raise HTTPException(status_code=500, detail=f"Agent workflow failed: {str(e)}")

class ResumeRequest(BaseModel):
    thread_id: str
    action: str # "APPROVE" or "REJECT"
    feedback: str = ""

@router.post("/resume")
async def resume_negotiation(request: ResumeRequest) -> Dict[str, Any]:
    """
    Resumes a paused workflow with human input.
    """
    config = {"configurable": {"thread_id": request.thread_id}}
    
    # Send the "Command" to resume from interrupt
    # In LangGraph 0.2+, we use update_state or just invoke with Command?
    # Actually, simpler: we update the state with the human result, then invoke(None) to continue.
    
    from langgraph.types import Command
    
    try:
        # We find the paused command and resume
        # For simplicity in this demo, we'll verify it's paused
        snapshot = negotiation_graph.get_state(config)
        if not snapshot.next:
             return {"status": "error", "message": "Thread is not paused."}
             
        # Resume with the input expected by 'interrupt'
        result = await negotiation_graph.ainvoke(
             Command(resume={"status": request.action, "feedback": request.feedback}),
             config=config
        )
        
        return {
            "status": "completed",
            "strategy": result.get("strategy_decision"),
            "redline": result.get("proposed_redline")
        }
    except Exception as e:
        # Again, check if paused again (multi-stage approval)
        snapshot = negotiation_graph.get_state(config)
        if snapshot.next:
             return {"status": "paused", "message": "More approval needed."}
@router.get("/thread/{thread_id}")
async def get_thread_state(thread_id: str) -> Dict[str, Any]:
    """
    Retrieves the current state of a negotiation thread.
    """
    config = {"configurable": {"thread_id": thread_id}}
    
    try:
        snapshot = negotiation_graph.get_state(config)
        if not snapshot.values:
            # If no LangGraph state, check if we have SQL data to at least show the page
            # For now, return empty-ish state so UI doesn't 404
            return {"status": "inactive", "messages": []}
            
        return {
            "status": "active" if not snapshot.next else "paused",
            "messages": snapshot.values.get("messages", []),
            "current_context": {
                "strategy": snapshot.values.get("strategy_decision"),
                "reasoning": snapshot.values.get("reasoning"),
                "redline": snapshot.values.get("proposed_redline"),
                "approval_status": snapshot.values.get("human_approval_status")
            }
        }
    except Exception as e:
        # If ID is invalid or other error
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/negotiations")
async def list_negotiations() -> List[Dict[str, Any]]:
    """
    Lists all active negotiations from the database.
    """
    from app.database import get_session
    from app.models import Negotiation
    from sqlalchemy.future import select
    from sqlalchemy.orm import selectinload
    
    # Manually creating session since we are not using Depends() in this file yet usually
    # But better to just use async context manager for simplicity here since 
    # we didn't set up full Dependency Injection in this file's signature
    from app.database import engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        # Fetch negotiations with related Contract and Supplier
        stmt = select(Negotiation).options(
            selectinload(Negotiation.contract).selectinload(Contract.supplier)
        )
        result = await session.execute(stmt)
        negotiations = result.scalars().all()
        
        return [
            {
                "id": str(n.id), # This maps to thread_id
                "supplier": n.contract.supplier.name if n.contract and n.contract.supplier else "Unknown",
                "contract_title": n.contract.title if n.contract else "Untitled",
                "status": n.status,
                "strategy": n.strategy,
                "risk_score": n.contract.supplier.risk_score if n.contract and n.contract.supplier else 0.0,
                "last_update": n.created_at.isoformat()
            }
            for n in negotiations
        ]
