import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.agent.nodes import human_review_gatekeeper
from app.agent.state import NegotiationState

@pytest.mark.asyncio
async def test_gatekeeper_autonomous_no_trigger():
    # Setup state
    state: NegotiationState = {
        "agency_level": "AUTONOMOUS",
        "human_approval_status": "",
        "reasoning": "Standard stuff."
    }
    
    # Run Node
    result = await human_review_gatekeeper(state)
    
    # Assert
    assert result["human_approval_status"] == "AUTO_APPROVED"

@pytest.mark.asyncio
async def test_gatekeeper_strict_mode_interrupt():
    # Setup state
    state: NegotiationState = {
        "agency_level": "STRICT",
        "human_approval_status": "",
        "reasoning": "High stakes."
    }
    
    # We expect an interrupt (which is implemented as raising a GraphInterrupt in recent LangGraph versions, 
    # but the `interrupt` function returns the resumed value when re-executed. 
    # Testing `interrupt` in isolation usually involves mocking the interrupt function provided by langgraph.
    
    with patch("app.agent.nodes.interrupt") as mock_interrupt:
        mock_interrupt.return_value = {"status": "APPROVED", "feedback": "Good job."} # Mock the RESUMED value
        
        # When called in a normal python context, interrupt() executes.
        # However, checking if it *halts* requires running inside the Graph.
        # For unit testing the NODE logic, we just check if it CALLED interrupt.
        
        result = await human_review_gatekeeper(state)
        
        assert mock_interrupt.called
        assert result["human_approval_status"] == "APPROVED"
        assert result["human_feedback"] == "Good job."

@pytest.mark.asyncio
async def test_gatekeeper_approved_skip():
    # Setup state: Already approved
    state: NegotiationState = {
        "agency_level": "STRICT",
        "human_approval_status": "APPROVED",
        "reasoning": "Checked."
    }
    
    result = await human_review_gatekeeper(state)
    assert result["human_approval_status"] == "PROCESSED"
