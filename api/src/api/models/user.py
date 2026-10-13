from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """
    User model representing an explorer in the Novias del Gato digital ecosystem.
    """

    id: UUID = Field(..., description="Unique identifier for the user.")
    name: str = Field(..., description="Full name of the user.", min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Email address of the user.")
    trust_score: float = Field(
        ...,
        description="Reputational metric scaling from 0.0 (untrusted) to 1.0 (highly reliable).",
        ge=0.0,
        le=1.0,
    )
    captured_count: int = Field(
        ..., description="Total number of unique sculptures verified by the user.", ge=0
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Juan Perez",
                "email": "juan.perez@gmail.com",
                "trust_score": 0.85,
                "captured_count": 12,
            }
        }
    }
