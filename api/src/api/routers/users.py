from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import EmailStr, HttpUrl, TypeAdapter
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db_session
from api.db_models.checkin import CheckInDB
from api.db_models.user import UserDB
from api.models.checkin import CheckInRecord
from api.models.user import User
from api.routers.deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

email_adapter = TypeAdapter(EmailStr)
http_url_adapter = TypeAdapter(HttpUrl)


@router.get(
    "/me",
    response_model=User,
    summary="Retrieve Current User Profile",
    description="Get details about the authenticated user, including their community trust score.",
)
async def get_my_profile(
    current_user: Annotated[UserDB, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    # Calculate count of unique verified captures
    count_stmt = select(func.count(CheckInDB.id)).where(CheckInDB.user_id == current_user.id)
    result = await db.execute(count_stmt)
    captured_count = result.scalar() or 0

    return User(
        id=current_user.id,
        name=current_user.name,
        email=email_adapter.validate_python(current_user.email),
        trust_score=current_user.trust_score,
        captured_count=captured_count,
    )


@router.get(
    "/me/collection",
    response_model=list[CheckInRecord],
    summary="Get User's Unlocked Sculptures",
    description="Returns the user's progress tracking which cat sculptures they have successfully captured.",
)
async def get_my_collection(
    current_user: Annotated[UserDB, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[CheckInRecord]:
    stmt = (
        select(CheckInDB)
        .where(CheckInDB.user_id == current_user.id)
        .order_by(CheckInDB.captured_at.desc())
    )
    result = await db.execute(stmt)
    check_ins = result.scalars().all()

    return [
        CheckInRecord(
            sculpture_id=item.sculpture_id,
            unlocked_at=item.captured_at,
            checkin_photo_url=(
                http_url_adapter.validate_python(item.photo_url) if item.photo_url else None
            ),
            similarity_score=item.similarity_score,
        )
        for item in check_ins
    ]
