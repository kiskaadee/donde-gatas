import uuid

import pytest
from pydantic import ValidationError

from api.models.checkin import CheckInResponse
from api.models.sculpture import Sculpture, SculptureDetails, SculptureStatus
from api.models.ticket import ReportVerificationRequest, Ticket, TicketStatus
from api.models.user import User


def test_user_model_valid():
    user = User(
        id=uuid.uuid4(),
        name="María del Rosario",
        email="maria@example.com",
        trust_score=0.8,
        captured_count=5,
    )
    assert user.name == "María del Rosario"
    assert user.trust_score == 0.8


def test_user_model_invalid_trust_score():
    with pytest.raises(ValidationError):
        User(
            id=uuid.uuid4(),
            name="Test",
            email="test@example.com",
            trust_score=1.5,  # Exceeds 1.0 limit
            captured_count=0,
        )


def test_sculpture_model_valid():
    sculpture = Sculpture(
        id=uuid.uuid4(),
        name="La Gata Ilustrada",
        artist="Lucy Tejada",
        year=2006,
        latitude=3.4516,
        longitude=-76.5326,
        status=SculptureStatus.ON_SITE,
    )
    assert sculpture.name == "La Gata Ilustrada"
    assert sculpture.status == SculptureStatus.ON_SITE


def test_sculpture_details_inheritance():
    details = SculptureDetails(
        id=uuid.uuid4(),
        name="La Novia Dulce",
        artist="Lorena Espitia",
        year=2006,
        latitude=3.4501,
        longitude=-76.5332,
        status=SculptureStatus.ON_SITE,
        description="Sculpture decorated with sweets.",
        audio_url="https://cdn.gatos.cali.gov.co/audio/novia.mp3",  # type: ignore[arg-type]
        unlocked_content="Cultural history unlocked.",
    )
    assert str(details.audio_url) == "https://cdn.gatos.cali.gov.co/audio/novia.mp3"


def test_checkin_similarity_bounds():
    with pytest.raises(ValidationError):
        CheckInResponse(
            success=True,
            similarity_score=1.2,  # Exceeds 1.0 limit
        )


def test_ticket_model_and_verification():
    ticket_id = uuid.uuid4()
    reporter_id = uuid.uuid4()
    sculpture_id = uuid.uuid4()

    ticket = Ticket(
        id=ticket_id,
        reporter_id=reporter_id,
        sculpture_id=sculpture_id,
        latitude=3.45,
        longitude=-76.53,
        reported_status=SculptureStatus.MOVED,
        status=TicketStatus.PENDING,
        created_at="2026-10-13T10:00:00Z",  # type: ignore[arg-type]
    )
    assert ticket.status == TicketStatus.PENDING

    req = ReportVerificationRequest(
        status=TicketStatus.APPROVED, notes="Verified by site inspection"
    )
    assert req.status == TicketStatus.APPROVED
