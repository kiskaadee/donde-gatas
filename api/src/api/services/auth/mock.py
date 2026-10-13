from api.services.auth.provider import AuthUserIdentity, IdentityProvider


class MockDevAdapter(IdentityProvider):
    """
    Mock identity provider for local development, tests, and CI.
    Bypasses external network calls to Google/OAuth endpoints.
    """

    def __init__(
        self, default_email: str = "explorer@cali.gov.co", default_name: str = "Test Explorer"
    ):
        self.default_email = default_email
        self.default_name = default_name

    async def verify_token(self, token: str) -> AuthUserIdentity:
        if token == "invalid-token":
            raise ValueError("Invalid mock authentication token provided.")

        # In dev/mock mode, token can optionally be formatted as "email:name"
        if ":" in token and "@" in token:
            parts = token.split(":", 1)
            email, name = parts[0], parts[1]
            return AuthUserIdentity(
                email=email,
                name=name,
                provider_user_id=f"mock-{email}",
            )

        return AuthUserIdentity(
            email=self.default_email,
            name=self.default_name,
            provider_user_id="mock-user-12345",
        )
