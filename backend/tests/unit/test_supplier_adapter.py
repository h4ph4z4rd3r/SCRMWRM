import pytest
from app.supplier.adapters.mock import MockDataProvider

@pytest.mark.asyncio
async def test_mock_financial_health_high_risk():
    provider = MockDataProvider()
    # Trigger High Risk
    data = await provider.get_financial_health("999123456")
    assert data["risk_class"] == "High"
    assert data["financial_stress_score"] <= 30

@pytest.mark.asyncio
async def test_mock_financial_health_stable():
    provider = MockDataProvider()
    # Default trigger
    data = await provider.get_financial_health("123456789")
    assert data["risk_class"] == "Low"
    assert data["financial_stress_score"] > 80

@pytest.mark.asyncio
async def test_mock_compliance_sanctioned():
    provider = MockDataProvider()
    result = await provider.check_compliance("Bad Actor Corp", "KP") # North Korea
    assert result["sanctions_flag"] is True

@pytest.mark.asyncio
async def test_mock_news_sentiment():
    provider = MockDataProvider()
    news = await provider.get_market_news("Risky Corp")
    assert len(news) > 0
    assert news[0]["sentiment"] == "negative"
