from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl

from api.models.sculpture import SculptureStatus


class TicketStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Ticket(BaseModel):
    """
    Ticket model representing a crowdsourced sculpture location report.
    """

    id: UUID = Field(..., description="Unique identifier for the report ticket.")
    reporter_id: UUID = Field(..., description="User ID of the reporter.")
    sculpture_id: UUID = Field(..., description="ID of the reported sculpture.")
    latitude: float = Field(..., description="GPS Latitude reported.", ge=-90.0, le=90.0)
    longitude: float = Field(..., description="GPS Longitude reported.", ge=-180.0, le=180.0)
    reported_status: SculptureStatus = Field(
        ..., description="The observed status of the sculpture."
    )
    photo_url: HttpUrl | None = Field(
        default=None, description="Verification photo of the site / pedestal."
    )
    description: str | None = Field(
        default=None,
        description="Additional context or details regarding the status.",
        max_length=500,
    )
    status: TicketStatus = Field(..., description="Resolution status of the ticket.")
    created_at: datetime = Field(..., description="Timestamp of when the ticket was submitted.")
    resolved_at: datetime | None = Field(
        default=None, description="Timestamp of when the ticket was approved/rejected."
    )
    notes: str | None = Field(
        default=None,
        description="Moderator resolution comments or verification notes.",
        max_length=300,
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "345e6789-e89b-12d3-a456-426614174000",
                "reporter_id": "123e4567-e89b-12d3-a456-426614174000",
                "sculpture_id": "234e5678-e89b-12d3-a456-426614174000",
                "latitude": 3.4515,
                "longitude": -76.5320,
                "reported_status": "moved",
                "photo_url": "https://cdn.gatos.cali.gov.co/uploads/report_8321.jpg",
                "description": "Under construction for street repairs. Pedestal is empty.",
                "status": "pending",
                "created_at": "2026-05-30T11:00:00Z",
                "resolved_at": None,
                "notes": None,
            }
        }
    }


class ReportVerificationRequest(BaseModel):
    """
    Request model used by moderators to resolve (verify) a report ticket.
    """

    status: TicketStatus = Field(
        ..., description="New status to set for the ticket (approved or rejected)."
    )
    notes: str | None = Field(
        default=None, description="Optional notes explaining the decision.", max_length=300
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "approved",
                "notes": "Verified via municipal service coordinates.",
            }
        }
    }
