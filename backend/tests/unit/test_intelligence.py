import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from app.supplier.intelligence import SupplierIntelligenceService
from app.models import Supplier

@pytest.mark.asyncio
async def test_intelligence_flow(mocker):
    # 1. Mock DB Session (AsyncMock because we use await session.xxx)
    mock_session = AsyncMock()
    mock_supplier = Supplier(id=uuid4(), name="Test Corp", lei="999000000")
    
    # Configure get return value
    # For AsyncMock, calling the method returns an awaitable. 
    # To set the RESULT of the awaitable, we set return_value.
    mock_session.get.return_value = mock_supplier
    
    # 2. Mock LLM Client
    mock_llm = AsyncMock()
    mock_llm.generate_json.return_value = {
        "news_sentiment_score": -0.5,
        "risk_summary": "Bad news detected.",
        "recommended_action": "HOLD"
    }
    mocker.patch("app.supplier.intelligence.get_llm_client", return_value=mock_llm)
    
    # 3. Mock Data Provider
    mock_provider = AsyncMock()
    mock_provider.get_financial_health.return_value = {"financial_stress_score": 20, "credit_rating": "CC"}
    mock_provider.get_market_news.return_value = [{"sentiment": "negative"}]
    mock_provider.check_compliance.return_value = {"sanctions_flag": False}
    
    mocker.patch("app.supplier.intelligence.get_supplier_data_provider", return_value=mock_provider)
    
    # Run Service
    service = SupplierIntelligenceService()
    risk_profile = await service.update_supplier_risk_profile(mock_session, mock_supplier.id)
    
    # Assertions
    # 1. Check if LLM was called with data
    assert mock_llm.generate_json.called
    user_message = mock_llm.generate_json.call_args[0][0][0].content
    assert "--- FINANCIALS ---" in user_message
    
    # 2. Check Risk Profile creation
    assert risk_profile.supplier_id == mock_supplier.id
    assert risk_profile.financial_stress_score == 20
    assert risk_profile.news_sentiment_score == -0.5
    
    # 3. Check DB commit
    assert mock_session.add.call_count >= 2 # Profile + Supplier update
    assert mock_session.commit.called
