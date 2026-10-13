from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class AuthUserIdentity:
    """
    Normalized user identity returned by any identity provider.
    """

    email: str
    name: str
    provider_user_id: str
    avatar_url: str | None = None


class IdentityProvider(Protocol):
    """
    Contract for pluggable SSO Identity Providers (Google, Authelia, Mock, etc.).
    """

    async def verify_token(self, token: str) -> AuthUserIdentity:
        """
        Verify external provider token and return normalized identity.
        Raises ValueError or equivalent on invalid or expired token.
        """
        ...
