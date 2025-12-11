import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from app.agent.graph import negotiation_graph
from app.agent.state import NegotiationState

@pytest.mark.asyncio
async def test_agent_graph_end_to_end_flow(mocker):
    """
    Verifies that the graph transitions correctly through all nodes:
    Lawyer -> Analyst -> Negotiator -> Gatekeeper -> Scribe.
    """
    
    # 1. Mock the Services used inside the nodes
    # We need to mock the functions imported in 'app.agent.nodes'
    # Since nodes.py initializes services globally (policy_evaluator, etc.), 
    # we need to patch those instances or their methods.
    
    # Mock PolicyEvaluator
    mock_policy_eval = AsyncMock()
    mock_policy_eval.evaluate.return_value = MagicMock(dict=lambda: {"status": "NON_COMPLIANT", "score": 0})
    mocker.patch("app.agent.nodes.policy_evaluator", mock_policy_eval)
    
    # Mock SupplierIntelligenceService
    mock_supplier_svc = AsyncMock()
    mock_supplier_svc.update_supplier_risk_profile.return_value = MagicMock(dict=lambda: {"financial_score": 50})
    mocker.patch("app.agent.nodes.supplier_service", mock_supplier_svc)
    
    # Mock LLM (for Strategy and Scribe)
    mock_llm = AsyncMock()
    # Strategy response
    mock_llm.generate_json.return_value = {"decision": "COUNTER", "reasoning": "Policy violation."}
    # Scribe response
    mock_llm.generate_response.return_value = "New draft clause text."
    mocker.patch("app.agent.nodes.llm", mock_llm)
    
    # Mock DB Session (get_session)
    # The nodes use 'async for session in get_session():'
    # We need to mock the generator.
    mock_session = AsyncMock()
    mock_session.exec.return_value.first.return_value = MagicMock(text_content="Policy Text") # Mock Policy fetch
    
    async def mock_get_session():
        yield mock_session
        
    mocker.patch("app.agent.nodes.get_session", mock_get_session)

    # 2. Setup Initial State
    initial_state: NegotiationState = {
        "contract_id": str(uuid4()),
        "supplier_id": str(uuid4()),
        "current_clause_text": "Payment Net 90",
        "agency_level": "AUTONOMOUS", # Skip HITL for this test
        "human_approval_status": "PENDING"
    }
    
    # 3. Run Graph
    # We use ainvoke with config for checkpointer
    final_state = await negotiation_graph.ainvoke(
        initial_state, 
        config={"configurable": {"thread_id": "integration_test_1"}}
    )
    
    # 4. Assertions
    
    # Check if Lawyer ran
    assert final_state["policy_analysis"]["status"] == "NON_COMPLIANT"
    
    # Check if Analyst ran
    assert final_state["risk_profile"]["financial_score"] == 50
    
    # Check if Negotiator ran
    assert final_state["strategy_decision"] == "COUNTER"
    assert final_state["reasoning"] == "Policy violation."
    
    # Check if Scribe ran (should be triggered by COUNTER decision)
    assert final_state["proposed_redline"] == "New draft clause text."
    
    # Check HITL status (Should be auto-approved due to Autonomous level mock logic if implemented simpler, 
    # but wait, Gatekeeper logic for Autonomous defaults to False needs_review unless trigger keyword found.
    # Our prompt didn't have trigger keyword. So it should Auto Approve.)
    assert final_state["human_approval_status"] == "AUTO_APPROVED"
