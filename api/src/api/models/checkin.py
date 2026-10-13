from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class CheckInRecord(BaseModel):
    """
    CheckInRecord representing a successful user capture of a sculpture.
    """

    sculpture_id: UUID = Field(..., description="The ID of the sculpture captured.")
    unlocked_at: datetime = Field(..., description="Timestamp of when the sculpture was captured.")
    checkin_photo_url: HttpUrl | None = Field(
        default=None, description="URL of the photo uploaded during check-in."
    )
    similarity_score: float = Field(
        ...,
        description="Visual recognition similarity score between the uploaded photo and the target model.",
        ge=0.0,
        le=1.0,
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "sculpture_id": "234e5678-e89b-12d3-a456-426614174000",
                "unlocked_at": "2026-05-30T10:15:30Z",
                "checkin_photo_url": "https://cdn.gatos.cali.gov.co/uploads/checkin_9823.jpg",
                "similarity_score": 0.92,
            }
        }
    }


class CheckInResponse(BaseModel):
    """
    Response model returned after a check-in verification request.
    """

    success: bool = Field(
        ..., description="Indicates if the visual check-in met threshold requirements."
    )
    similarity_score: float = Field(
        ..., description="The visual similarity rating from the recognition engine.", ge=0.0, le=1.0
    )
    unlocked_content: str | None = Field(
        default=None, description="Unlocked cultural details of the sculpture, if success is true."
    )
    reward_badge: str | None = Field(
        default=None, description="Name of the badge unlocked by this capture, if any."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": True,
                "similarity_score": 0.92,
                "unlocked_content": "This sculpture was crafted in tribute to the traditional festival of Macetas.",
                "reward_badge": "First Sighting",
            }
        }
    }
