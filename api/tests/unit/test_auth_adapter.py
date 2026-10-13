import pytest

from api.services.auth.mock import MockDevAdapter
from api.services.auth.service import AuthService


@pytest.mark.asyncio
async def test_mock_dev_adapter_default():
    adapter = MockDevAdapter()
    identity = await adapter.verify_token("any-token")
    assert identity.email == "explorer@cali.gov.co"
    assert identity.provider_user_id == "mock-user-12345"


@pytest.mark.asyncio
async def test_mock_dev_adapter_custom_token():
    adapter = MockDevAdapter()
    identity = await adapter.verify_token("ana@gmail.com:Ana Gomez")
    assert identity.email == "ana@gmail.com"
    assert identity.name == "Ana Gomez"
    assert identity.provider_user_id == "mock-ana@gmail.com"


@pytest.mark.asyncio
async def test_mock_dev_adapter_invalid_token():
    adapter = MockDevAdapter()
    with pytest.raises(ValueError, match="Invalid mock"):
        await adapter.verify_token("invalid-token")


def test_auth_service_jwt_lifecycle():
    auth_service = AuthService(provider=MockDevAdapter())
    login_resp = auth_service.create_access_token(user_id="user-123", email="user@example.com")

    assert login_resp.token_type == "Bearer"
    assert login_resp.expires_in > 0

    decoded = auth_service.decode_access_token(login_resp.access_token)
    assert decoded["sub"] == "user-123"
    assert decoded["email"] == "user@example.com"
