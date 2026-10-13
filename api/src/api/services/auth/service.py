from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from api.core.config import settings
from api.models.auth import LoginResponse
from api.services.auth.mock import MockDevAdapter
from api.services.auth.provider import AuthUserIdentity, IdentityProvider


class AuthService:
    """
    Core authentication service responsible for token issuance, JWT verification,
    and delegating SSO validation to an IdentityProvider adapter.
    """

    def __init__(self, provider: IdentityProvider | None = None):
        if provider is not None:
            self.provider = provider
        elif settings.ENV in ("test", "development"):
            self.provider = MockDevAdapter()
        else:
            from api.services.auth.google import GoogleOAuthAdapter

            self.provider = GoogleOAuthAdapter(client_id=settings.GOOGLE_CLIENT_ID)

    def create_access_token(self, user_id: str, email: str) -> LoginResponse:
        """
        Create a signed JWT access token for the given user.
        """
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.now(UTC) + expires_delta

        payload: dict[str, Any] = {
            "sub": str(user_id),
            "email": email,
            "exp": expire,
            "iat": datetime.now(UTC),
        }

        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

        return LoginResponse(
            access_token=token,
            token_type="Bearer",
            expires_in=int(expires_delta.total_seconds()),
        )

    def decode_access_token(self, token: str) -> dict[str, Any]:
        """
        Decode and validate a JWT access token.
        Raises jwt.PyJWTError on invalid or expired token.
        """
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

    async def authenticate_sso(self, id_token: str) -> AuthUserIdentity:
        """
        Validate an external token using the configured IdentityProvider.
        """
        return await self.provider.verify_token(id_token)
