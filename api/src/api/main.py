from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.models.auth import DevTokenRequest, LoginResponse
from api.routers import sculptures
from api.services.auth.service import AuthService

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Digital ecosystem backend for Cali's public art (Novias del Gato).",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sculptures.router)

auth_service = AuthService()


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "env": settings.ENV,
    }


@app.post(
    "/auth/dev-token",
    response_model=LoginResponse,
    tags=["Authentication"],
    summary="Development SSO Bypass Token Generation",
)
async def generate_dev_token(payload: DevTokenRequest) -> LoginResponse:
    """
    Generate signed JWT for testing without contacting external OAuth providers.
    Available only when ENV is not 'production'.
    """
    if settings.ENV == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development token generation disabled in production environment.",
        )

    # Use deterministic mock ID based on email
    import hashlib
    import uuid

    deterministic_uuid = uuid.UUID(hashlib.md5(payload.email.encode("utf-8")).hexdigest())

    return auth_service.create_access_token(
        user_id=str(deterministic_uuid),
        email=payload.email,
    )
