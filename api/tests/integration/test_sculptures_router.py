import uuid

import pytest
from httpx import AsyncClient

from api.database.seed import INITIAL_SCULPTURES


@pytest.mark.asyncio
async def test_list_sculptures_endpoint(async_client: AsyncClient):
    response = await async_client.get("/sculptures")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3

    # Check that our seeded sculptures are present
    names = {item["name"] for item in data}
    for seeded in INITIAL_SCULPTURES:
        assert seeded["name"] in names

    # Verify schema fields and coordinates on each sculpture
    for item in data:
        assert "id" in item
        assert "name" in item
        assert "artist" in item
        assert "year" in item
        assert "latitude" in item
        assert "longitude" in item
        assert "status" in item
        # Cali bounding box check
        assert 3.30 <= item["latitude"] <= 3.60
        assert -76.60 <= item["longitude"] <= -76.40
        assert item["status"] in ("on-site", "moved", "missing")


@pytest.mark.asyncio
async def test_get_sculpture_by_id_success(async_client: AsyncClient):
    target_id = str(INITIAL_SCULPTURES[0]["id"])
    response = await async_client.get(f"/sculptures/{target_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == target_id
    assert data["name"] == INITIAL_SCULPTURES[0]["name"]
    assert data["artist"] == INITIAL_SCULPTURES[0]["artist"]
    assert data["year"] == INITIAL_SCULPTURES[0]["year"]
    assert data["description"] == INITIAL_SCULPTURES[0]["description"]
    assert data["audio_url"] == INITIAL_SCULPTURES[0]["audio_url"]
    assert data["unlocked_content"] == INITIAL_SCULPTURES[0]["unlocked_content"]


@pytest.mark.asyncio
async def test_get_sculpture_by_id_not_found(async_client: AsyncClient):
    non_existent_id = uuid.uuid4()
    response = await async_client.get(f"/sculptures/{non_existent_id}")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Sculpture not found."


@pytest.mark.asyncio
async def test_get_sculpture_by_id_invalid_uuid(async_client: AsyncClient):
    response = await async_client.get("/sculptures/invalid-uuid-1234")
    assert response.status_code == 422
