import random
from typing import Dict, List, Any
from .base import ExternalDataProvider

class MockDataProvider(ExternalDataProvider):
    """
    Mock Data Provider for testing and development.
    Generates realistic scenarios based on triggers in the company name or DUNS.
    """

    async def get_financial_health(self, duns_number: str) -> Dict[str, Any]:
        # Scenario: "999..." is always High Risk
        if duns_number.startswith("999"):
            return {
                "financial_stress_score": 10, # Very Bad (1-100 scale where 1 is bad? D&B varies. Let's assume 100 is best)
                # Correction: D&B Viability Rating: 1 (best) - 9 (worst). Or Failure Score 1 (high risk) - 100 (low risk).
                # Let's standardize on: 1-100 where 100 IS GOOD / SAFE.
                "financial_stress_score": 25, # High Risk
                "credit_rating": "CC",
                "risk_class": "High"
            }
        else:
            return {
                "financial_stress_score": 85, # Stability
                "credit_rating": "5A1",
                "risk_class": "Low"
            }

    async def get_market_news(self, company_name: str) -> List[Dict[str, str]]:
        if "Risky" in company_name or "Volatile" in company_name:
            return [
                {"title": f"{company_name} faces class action lawsuit over fraud", "source": "MockNews", "sentiment": "negative"},
                {"title": f"CEO of {company_name} steps down amid scandal", "source": "MockNews", "sentiment": "negative"}
            ]
        elif "Green" in company_name:
             return [
                {"title": f"{company_name} wins sustainability award", "source": "MockNews", "sentiment": "positive"},
                {"title": f"{company_name} expands into new markets", "source": "MockNews", "sentiment": "positive"}
            ]
        else:
            return []

    async def check_compliance(self, company_name: str, country_code: str) -> Dict[str, Any]:
        # Scenario: North Korea or Russia or specific name
        if country_code in ["KP", "RU", "IR"] or "Sanctioned" in company_name:
            return {
                "sanctions_flag": True,
                "list_match": "OFAC SDN List"
            }
        return {
            "sanctions_flag": False,
            "list_match": None
        }
