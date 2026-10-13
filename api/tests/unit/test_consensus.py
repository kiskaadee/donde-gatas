from datetime import UTC, datetime

from api.services.consensus import (
    ConsensusDecision,
    SightingReport,
    adjust_trust_score,
    evaluate_reports,
    haversine_distance_meters,
    verify_velocity,
)


def test_haversine_distance():
    # Distance between two nearby points on Boulevard del Río (~160 meters)
    lat1, lon1 = 3.450143, -76.533282
    lat2, lon2 = 3.451600, -76.532600
    dist = haversine_distance_meters(lat1, lon1, lat2, lon2)
    assert 150 < dist < 180


def test_verify_velocity_plausible():
    # 200 meters in 60 seconds = 12 km/h (plausible walking/running speed)
    t1 = datetime(2026, 10, 13, 10, 0, 0, tzinfo=UTC)
    t2 = datetime(2026, 10, 13, 10, 1, 0, tzinfo=UTC)
    lat1, lon1 = 3.450143, -76.533282
    lat2, lon2 = 3.451600, -76.532600

    assert verify_velocity(lat1, lon1, t1, lat2, lon2, t2, max_kmh=120.0) is True


def test_verify_velocity_teleportation_rejected():
    # 5 km in 10 seconds = 1800 km/h (impossible, GPS spoofing)
    t1 = datetime(2026, 10, 13, 10, 0, 0, tzinfo=UTC)
    t2 = datetime(2026, 10, 13, 10, 0, 10, tzinfo=UTC)
    lat1, lon1 = 3.450143, -76.533282
    lat2, lon2 = 3.490000, -76.533282

    assert verify_velocity(lat1, lon1, t1, lat2, lon2, t2, max_kmh=120.0) is False


def test_evaluate_reports_auto_approve():
    # 4 distinct high-trust users reporting 'moved' within 10 meters of each other
    now = datetime.now(UTC)
    reports = [
        SightingReport(
            reporter_id=f"user-{i}",
            latitude=3.45160 + (i * 0.00005),
            longitude=-76.53260,
            reported_status="moved",
            trust_score=0.9,
            created_at=now,
        )
        for i in range(4)
    ]

    result = evaluate_reports(reports)
    assert result.decision == ConsensusDecision.AUTO_APPROVE
    assert result.distinct_reporters == 4
    assert result.consensus_status == "moved"
    assert result.confidence_score >= 3.0


def test_evaluate_reports_pending_moderation():
    # 2 users with moderate trust (total confidence ~1.6 < 3.0 threshold)
    now = datetime.now(UTC)
    reports = [
        SightingReport(
            reporter_id="user-1",
            latitude=3.45160,
            longitude=-76.53260,
            reported_status="missing",
            trust_score=0.8,
            created_at=now,
        ),
        SightingReport(
            reporter_id="user-2",
            latitude=3.45161,
            longitude=-76.53261,
            reported_status="missing",
            trust_score=0.8,
            created_at=now,
        ),
    ]

    result = evaluate_reports(reports)
    assert result.decision == ConsensusDecision.PENDING_MODERATION
    assert result.distinct_reporters == 2


def test_adjust_trust_score_bounds():
    # Boost clamping
    assert adjust_trust_score(0.98, verified_positive=True, boost=0.05) == 1.0

    # Penalty clamping
    assert adjust_trust_score(0.10, verified_positive=False, penalty=0.15) == 0.0

    # Normal increment
    assert adjust_trust_score(0.50, verified_positive=True, boost=0.05) == 0.55
