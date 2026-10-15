import pytest
from httpx import AsyncClient

from api.routers.deps import auth_service


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Novias del Gato" in data["service"]


@pytest.mark.asyncio
async def test_dev_token_endpoint(async_client: AsyncClient):
    payload = {"email": "carlos@example.com", "name": "Carlos Ruiz"}
    response = await async_client.post("/auth/dev-token", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"

    # Verify returned token with auth service
    decoded = auth_service.decode_access_token(data["access_token"])
    assert decoded["email"] == "carlos@example.com"
