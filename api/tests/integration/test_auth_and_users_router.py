import uuid

import pytest
from httpx import AsyncClient

from api.core.config import settings
from api.database.seed import INITIAL_SCULPTURES
from api.db_models.checkin import CheckInDB
from tests.conftest import TestAsyncSessionLocal


@pytest.mark.asyncio
async def test_auth_login_success(async_client: AsyncClient):
    payload = {"id_token": "valid-mock-token"}
    response = await async_client.post("/auth/login", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_auth_login_invalid_token(async_client: AsyncClient):
    payload = {"id_token": "invalid-token"}
    response = await async_client.post("/auth/login", json=payload)
    assert response.status_code == 401
    assert "Invalid token provided" in response.json()["detail"]


@pytest.mark.asyncio
async def test_dev_token_production_disabled(async_client: AsyncClient):
    original_env = settings.ENV
    try:
        settings.ENV = "production"
        payload = {"email": "blocked@cali.gov.co", "name": "Blocked"}
        response = await async_client.post("/auth/dev-token", json=payload)
        assert response.status_code == 403
        assert "disabled in production" in response.json()["detail"]
    finally:
        settings.ENV = original_env


@pytest.mark.asyncio
async def test_users_me_unauthorized(async_client: AsyncClient):
    # Missing header
    res1 = await async_client.get("/users/me")
    assert res1.status_code == 401

    # Invalid token
    res2 = await async_client.get("/users/me", headers={"Authorization": "Bearer bad.token.here"})
    assert res2.status_code == 401


@pytest.mark.asyncio
async def test_users_me_and_collection_flow(async_client: AsyncClient):
    test_email = f"explorer.{uuid.uuid4().hex[:8]}@example.com"
    token_resp = await async_client.post(
        "/auth/dev-token", json={"email": test_email, "name": "Collection Explorer"}
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Profile initially has 0 captures
    profile_resp = await async_client.get("/users/me", headers=headers)
    assert profile_resp.status_code == 200
    profile_data = profile_resp.json()
    assert profile_data["email"] == test_email
    assert profile_data["name"] == "Collection Explorer"
    assert profile_data["captured_count"] == 0
    user_id = uuid.UUID(profile_data["id"])

    # 2. Collection initially empty
    col_resp = await async_client.get("/users/me/collection", headers=headers)
    assert col_resp.status_code == 200
    assert col_resp.json() == []

    # 3. Add a check-in record directly via DB session
    sculpture_id = INITIAL_SCULPTURES[0]["id"]
    async with TestAsyncSessionLocal() as session:
        check_in = CheckInDB(
            user_id=user_id,
            sculpture_id=sculpture_id,
            photo_url="https://cdn.gatos.cali.gov.co/uploads/test.jpg",
            similarity_score=0.92,
        )
        session.add(check_in)
        await session.commit()

    # 4. Collection now has 1 capture
    col_resp2 = await async_client.get("/users/me/collection", headers=headers)
    assert col_resp2.status_code == 200
    items = col_resp2.json()
    assert len(items) == 1
    assert items[0]["sculpture_id"] == str(sculpture_id)
    assert items[0]["similarity_score"] == 0.92
    assert items[0]["checkin_photo_url"] == "https://cdn.gatos.cali.gov.co/uploads/test.jpg"

    # 5. Profile captured_count reflects the new capture
    profile_resp2 = await async_client.get("/users/me", headers=headers)
    assert profile_resp2.status_code == 200
    assert profile_resp2.json()["captured_count"] == 1
