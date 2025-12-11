from abc import ABC, abstractmethod
from typing import Dict, List, Any

class ExternalDataProvider(ABC):
    """
    Abstract Base Class for external supplier data providers.
    
    This interface unifies access to financial, news, and compliance data,
    allowing the system to switch between Mock, D&B, and other vendors easily.
    """

    @abstractmethod
    async def get_financial_health(self, duns_number: str) -> Dict[str, Any]:
        """
        Retrieve financial health indicators.

        Args:
            duns_number (str): The D-U-N-S Number (Unique identifier).

        Returns:
            Dict: {
                "financial_stress_score": int,
                "credit_rating": str,
                "revenue_currency": str,
                ...
            }
        """
        pass

    @abstractmethod
    async def get_market_news(self, company_name: str) -> List[Dict[str, str]]:
        """
        Retrieve recent market news headlines.

        Args:
            company_name (str): Name of the supplier.

        Returns:
            List[Dict]: [
                {"title": "...", "source": "...", "sentiment": "negative", "url": "..."}
            ]
        """
        pass

    @abstractmethod
    async def check_compliance(self, company_name: str, country_code: str) -> Dict[str, Any]:
        """
        Check against sanctions and PEP lists.

        Args:
            company_name (str): Name of the entity.
            country_code (str): ISO 3166-1 alpha-2 code (e.g., "DE", "US").

        Returns:
            Dict: {
                "sanctions_flag": bool,
                "list_match": Optional[str]
            }
        """
        pass
