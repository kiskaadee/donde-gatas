import struct
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from geoalchemy2.elements import WKBElement, WKTElement
from pydantic import HttpUrl, TypeAdapter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import get_db_session
from api.db_models.sculpture import SculptureDB
from api.models.sculpture import Sculpture, SculptureDetails, SculptureStatus

router = APIRouter(prefix="/sculptures", tags=["Sculptures"])

http_url_adapter = TypeAdapter(HttpUrl)


def extract_coordinates(location: object) -> tuple[float, float]:
    """
    Extract (longitude, latitude) from PostGIS WKBElement, WKTElement, or string representation.
    """
    if isinstance(location, WKTElement) or (isinstance(location, str) and "POINT" in location):
        raw_str = str(location).strip()
        coords_str = raw_str[raw_str.find("(") + 1 : raw_str.find(")")]
        lon, lat = map(float, coords_str.split())
        return lon, lat

    if isinstance(location, WKBElement):
        raw = location.data
        b = bytes.fromhex(raw) if isinstance(raw, str) else raw
        byteorder = "<" if b[0] == 1 else ">"
        geom_type = struct.unpack(byteorder + "I", b[1:5])[0]
        # Check for SRID flag (EWKB: 0x20000000)
        offset = 9 if (geom_type & 0x20000000) else 5
        lon, lat = struct.unpack(byteorder + "dd", b[offset : offset + 16])
        return lon, lat

    raise ValueError(f"Unsupported location geometry format: {type(location)}")


def to_sculpture_read(db_item: SculptureDB) -> Sculpture:
    lon, lat = extract_coordinates(db_item.location)
    return Sculpture(
        id=db_item.id,
        name=db_item.name,
        artist=db_item.artist,
        year=db_item.year,
        latitude=lat,
        longitude=lon,
        status=SculptureStatus(db_item.status),
    )


def to_sculpture_details(db_item: SculptureDB) -> SculptureDetails:
    lon, lat = extract_coordinates(db_item.location)
    audio_url = http_url_adapter.validate_python(db_item.audio_url) if db_item.audio_url else None
    return SculptureDetails(
        id=db_item.id,
        name=db_item.name,
        artist=db_item.artist,
        year=db_item.year,
        latitude=lat,
        longitude=lon,
        status=SculptureStatus(db_item.status),
        description=db_item.description,
        audio_url=audio_url,
        unlocked_content=db_item.unlocked_content,
    )


@router.get("", response_model=list[Sculpture], summary="List All Cat Sculptures")
async def list_sculptures(
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[Sculpture]:
    """
    Returns list of all sculptures with names, locations, and current status (Single Source of Truth).
    """
    query = select(SculptureDB).order_by(SculptureDB.name)
    result = await db.execute(query)
    sculptures_db = result.scalars().all()
    return [to_sculpture_read(item) for item in sculptures_db]


@router.get("/{id}", response_model=SculptureDetails, summary="Get Sculpture Details")
async def get_sculpture_by_id(
    id: UUID,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SculptureDetails:
    """
    Detailed information about a sculpture, historical context, artist, and unlockable audio guides.
    """
    sculpture = await db.get(SculptureDB, id)
    if not sculpture:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sculpture not found.",
        )
    return to_sculpture_details(sculpture)
