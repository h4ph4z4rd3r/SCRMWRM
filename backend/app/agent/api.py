from typing import Dict, Any
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
            return {"status": "empty", "messages": []}
            
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
        raise HTTPException(status_code=500, detail=str(e))
