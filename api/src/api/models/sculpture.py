from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class SculptureStatus(StrEnum):
    ON_SITE = "on-site"
    MOVED = "moved"
    MISSING = "missing"


class Sculpture(BaseModel):
    """
    Sculpture base model representing a public cat monument.
    """

    id: UUID = Field(..., description="Unique identifier for the sculpture.")
    name: str = Field(..., description="Name of the sculpture.", min_length=1)
    artist: str = Field(..., description="Artist who created the sculpture.", min_length=1)
    year: int = Field(..., description="Year the sculpture was created / installed.", ge=1900)
    latitude: float = Field(
        ..., description="GPS Latitude coordinate of the sculpture.", ge=-90.0, le=90.0
    )
    longitude: float = Field(
        ..., description="GPS Longitude coordinate of the sculpture.", ge=-180.0, le=180.0
    )
    status: SculptureStatus = Field(..., description="Operational status of the sculpture.")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "234e5678-e89b-12d3-a456-426614174000",
                "name": "La Novia Dulce",
                "artist": "Lorena Espitia",
                "year": 2006,
                "latitude": 3.450143,
                "longitude": -76.533282,
                "status": "on-site",
            }
        }
    }


class SculptureDetails(Sculpture):
    """
    Extended sculpture model containing cultural details, unlocked content, and audio resources.
    """

    description: str | None = Field(
        default=None, description="Public cultural description of the sculpture."
    )
    audio_url: HttpUrl | None = Field(
        default=None, description="Direct link to the audio guide resource."
    )
    unlocked_content: str | None = Field(
        default=None, description="Extended history/curation unlocked upon checking in."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "234e5678-e89b-12d3-a456-426614174000",
                "name": "La Novia Dulce",
                "artist": "Lorena Espitia",
                "year": 2006,
                "latitude": 3.450143,
                "longitude": -76.533282,
                "status": "on-site",
                "description": "Decorated with sweets and candies representing Cali's culinary traditions.",
                "audio_url": "https://cdn.gatos.cali.gov.co/audio/novia_dulce.mp3",
                "unlocked_content": "This sculpture was crafted in tribute to the traditional festival of Macetas.",
            }
        }
    }
