from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    Request model for Google SSO Authentication.
    """

    id_token: str = Field(..., description="The ID token returned by Google OAuth flow.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJpc3MiOiJodHRwczovL2FjY291bnRzLmdvb2dsZS5jb20iLCJzdWIiOiIxMjM0NTY3ODkwIiwiYXVkIjoiY2xpZW50X2lkIiwiZXhwIjoxNDY5NDkwMDAwfQ..."
            }
        }
    }


class LoginResponse(BaseModel):
    """
    Response model containing authentication JWT token details.
    """

    access_token: str = Field(
        ..., description="JWT access token for subsequent authenticated API requests."
    )
    token_type: str = Field("Bearer", description="The type of the returned access token.")
    expires_in: int = Field(..., description="The lifetime of the access token in seconds.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ...",
                "token_type": "Bearer",
                "expires_in": 3600,
            }
        }
    }


class DevTokenRequest(BaseModel):
    """
    Request model for development/testing SSO bypass.
    """

    email: str = Field(..., description="Email address for the mock test user.")
    name: str = Field("Local Explorer", description="Display name for the mock test user.")
