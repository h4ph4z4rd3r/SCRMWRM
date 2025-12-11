from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.agent.state import NegotiationState
from app.agent.nodes import policy_analysis_node, risk_analysis_node, strategy_node, drafting_node, human_review_gatekeeper

def build_negotiation_graph():
    """
    Constructs the LangGraph for the negotiation workflow.
    """
    workflow = StateGraph(NegotiationState)
    
    # Add Nodes
    workflow.add_node("lawyer", policy_analysis_node)
    workflow.add_node("analyst", risk_analysis_node)
    workflow.add_node("negotiator", strategy_node)
    workflow.add_node("gatekeeper", human_review_gatekeeper)
    workflow.add_node("scribe", drafting_node)
    
    # Define Edges
    # Start -> Lawyer (Check Policy)
    workflow.set_entry_point("lawyer")
    
    # Lawyer -> Analyst (Check Risk)
    workflow.add_edge("lawyer", "analyst")
    
    # Analyst -> Negotiator (Synthesize)
    workflow.add_edge("analyst", "negotiator")
    
    # Negotiator -> Gatekeeper (HITL Check)
    workflow.add_edge("negotiator", "gatekeeper")
    
    # Gatekeeper -> Scribe (Drafting)
    # The interrupt happens inside Gatekeeper. If it resumes, it goes to Scribe (if Approved)
    # Ideally we'd have conditional edges here: 
    # If Rejected -> End of Loop back?
    # For MVP: Proceed to Scribe. Scribe can check status.
    workflow.add_edge("gatekeeper", "scribe")
    
    # Scribe -> End
    workflow.add_edge("scribe", END)
    
    # Persistence is required for interrupts
    checkpointer = MemorySaver()
    
    return workflow.compile(checkpointer=checkpointer)

# Singleton instance
negotiation_graph = build_negotiation_graph()
