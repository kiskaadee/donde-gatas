import hashlib
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.config import settings
from api.database.session import get_db_session
from api.db_models.user import UserDB
from api.models.auth import DevTokenRequest, LoginRequest, LoginResponse
from api.routers.deps import auth_service

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Google SSO Authentication",
    description="Exchange a Google OAuth ID token for a system-issued JWT access token.",
)
async def login_user(
    payload: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    try:
        identity = await auth_service.authenticate_sso(payload.id_token)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token provided: {err}",
        ) from err

    # Provision or retrieve user
    result = await db.execute(select(UserDB).where(UserDB.email == identity.email))
    user = result.scalars().first()

    if not user:
        user_uuid = uuid.UUID(hashlib.md5(identity.email.encode("utf-8")).hexdigest())
        user = UserDB(
            id=user_uuid,
            name=identity.name,
            email=identity.email,
            trust_score=0.5,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return auth_service.create_access_token(
        user_id=str(user.id),
        email=user.email,
    )


@router.post(
    "/dev-token",
    response_model=LoginResponse,
    summary="Development SSO Bypass Token Generation",
    description="Generate signed JWT for testing without contacting external OAuth providers.",
)
async def generate_dev_token(
    payload: DevTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoginResponse:
    if settings.ENV == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Development token generation disabled in production environment.",
        )

    # Deterministic UUID based on email
    user_uuid = uuid.UUID(hashlib.md5(payload.email.encode("utf-8")).hexdigest())

    # Ensure user exists in database
    result = await db.execute(select(UserDB).where(UserDB.email == payload.email))
    user = result.scalars().first()

    if not user:
        user = UserDB(
            id=user_uuid,
            name=payload.name,
            email=payload.email,
            trust_score=0.5,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return auth_service.create_access_token(
        user_id=str(user.id),
        email=user.email,
    )
