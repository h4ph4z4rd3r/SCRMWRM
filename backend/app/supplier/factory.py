from app.core.config import settings
from .adapters.base import ExternalDataProvider
from .adapters.mock import MockDataProvider

def get_supplier_data_provider() -> ExternalDataProvider:
    """
    Factory function to return the configured ExternalDataProvider.
    """
    provider_type = settings.SUPPLIER_DATA_PROVIDER.lower()
    
    if provider_type == "mock":
        return MockDataProvider()
    # elif provider_type == "dnb":
    #     return DnBDirectProvider()
    else:
        # Default to mock for safety if misconfigured
        return MockDataProvider()
