import httpx

from api.services.auth.provider import AuthUserIdentity, IdentityProvider


class GoogleOAuthAdapter(IdentityProvider):
    """
    Google OAuth token verification adapter.
    """

    GOOGLE_TOKENINFO_URL = "https://oauth2.googleapis.com/tokeninfo"

    def __init__(self, client_id: str | None = None):
        self.client_id = client_id

    async def verify_token(self, token: str) -> AuthUserIdentity:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(self.GOOGLE_TOKENINFO_URL, params={"id_token": token})

            if response.status_code != 200:
                raise ValueError("Failed to verify Google ID token with upstream provider.")

            data = response.json()

            # Verify audience if client_id is configured
            if self.client_id and data.get("aud") != self.client_id:
                raise ValueError("Google ID token audience mismatch.")

            email = data.get("email")
            if not email:
                raise ValueError("Google ID token missing email address.")

            name = data.get("name", email.split("@")[0])
            sub = data.get("sub", "")
            picture = data.get("picture")

            return AuthUserIdentity(
                email=email,
                name=name,
                provider_user_id=sub,
                avatar_url=picture,
            )
