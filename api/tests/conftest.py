from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import app


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Test client for FastAPI ASGI endpoints.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
