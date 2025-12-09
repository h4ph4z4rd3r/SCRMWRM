import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from typing import Generator
from app.core.config import settings

# Note: We will import the 'app' object after the app structure is confirmed active
# For now, we mock the app import or use a placeholder if main.py is providing it
from main import app

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
async def async_client() -> Generator:
    """
    Fixture for creating an async HTTP client for integration tests.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
