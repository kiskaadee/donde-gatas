import struct
import uuid

import pytest
from geoalchemy2.elements import WKBElement, WKTElement

from api.db_models.sculpture import SculptureDB
from api.routers.sculptures import (
    extract_coordinates,
    to_sculpture_details,
    to_sculpture_read,
)


def test_extract_coordinates_from_wkt():
    wkt = WKTElement("POINT(-76.533282 3.450143)", srid=4326)
    lon, lat = extract_coordinates(wkt)
    assert abs(lon - (-76.533282)) < 1e-6
    assert abs(lat - 3.450143) < 1e-6


def test_extract_coordinates_from_wkb_ewkb():
    # Build standard EWKB for POINT(-76.533282 3.450143) SRID 4326
    # byteorder: 1 (little-endian), type: 0x20000001 (Point + EWKB), srid: 4326
    packed = struct.pack("<bIIdd", 1, 0x20000001, 4326, -76.533282, 3.450143)
    wkb = WKBElement(packed)
    lon, lat = extract_coordinates(wkb)
    assert abs(lon - (-76.533282)) < 1e-6
    assert abs(lat - 3.450143) < 1e-6


def test_extract_coordinates_unsupported_type():
    with pytest.raises(ValueError, match="Unsupported location geometry format"):
        extract_coordinates(12345)  # type: ignore[arg-type]


def test_to_sculpture_read_mapping():
    point = WKTElement("POINT(-76.5329 3.4508)", srid=4326)
    db_item = SculptureDB(
        id=uuid.uuid4(),
        name="La Gata Ilustrada",
        artist="Lucy Tejada",
        year=2006,
        description="A wonderful sculpture",
        audio_url="https://cdn.gatos.cali.gov.co/audio/test.mp3",
        unlocked_content="Secret lore",
        status="on-site",
        location=point,
        embedding=[0.0] * 1280,
    )
    read_model = to_sculpture_read(db_item)
    assert read_model.name == "La Gata Ilustrada"
    assert read_model.year == 2006
    assert abs(read_model.longitude - (-76.5329)) < 1e-6
    assert abs(read_model.latitude - 3.4508) < 1e-6


def test_to_sculpture_details_mapping():
    point = WKTElement("POINT(-76.5326 3.4516)", srid=4326)
    db_item = SculptureDB(
        id=uuid.uuid4(),
        name="La Gata Ceremonial",
        artist="José Horacio Martínez",
        year=2006,
        description="Pre-Columbian motifs",
        audio_url="https://cdn.gatos.cali.gov.co/audio/ceremonial.mp3",
        unlocked_content="Gold lore",
        status="moved",
        location=point,
        embedding=[0.0] * 1280,
    )
    details_model = to_sculpture_details(db_item)
    assert details_model.name == "La Gata Ceremonial"
    assert details_model.status.value == "moved"
    assert details_model.description == "Pre-Columbian motifs"
    assert str(details_model.audio_url) == "https://cdn.gatos.cali.gov.co/audio/ceremonial.mp3"
    assert details_model.unlocked_content == "Gold lore"
