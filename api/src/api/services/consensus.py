import math
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from api.core.config import settings


class ConsensusDecision(StrEnum):
    AUTO_APPROVE = "auto_approve"
    PENDING_MODERATION = "pending_moderation"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True)
class SightingReport:
    """
    Input data representing a single user report for consensus calculation.
    """

    reporter_id: str
    latitude: float
    longitude: float
    reported_status: str
    trust_score: float
    created_at: datetime


@dataclass(frozen=True)
class ConsensusResult:
    """
    Outcome of evaluating a cluster of reports against the Oracle's consensus rules.
    """

    decision: ConsensusDecision
    confidence_score: float
    distinct_reporters: int
    centroid_latitude: float
    centroid_longitude: float
    consensus_status: str


def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two geographic points in meters.
    """
    earth_radius_m = 6_371_000.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return earth_radius_m * c


def verify_velocity(
    lat1: float,
    lon1: float,
    t1: datetime,
    lat2: float,
    lon2: float,
    t2: datetime,
    max_kmh: float = settings.MAX_PLAUSIBLE_VELOCITY_KMH,
) -> bool:
    """
    Verify that the speed required to travel between two consecutive submissions
    does not exceed the maximum plausible urban velocity (default 120 km/h).
    Returns True if physically plausible, False if likely spoofed.
    """
    time_delta_seconds = abs((t2 - t1).total_seconds())
    if time_delta_seconds <= 0:
        # Simultaneous submissions at distinct locations are physically impossible
        return (lat1 == lat2) and (lon1 == lon2)

    distance_m = haversine_distance_meters(lat1, lon1, lat2, lon2)
    speed_mps = distance_m / time_delta_seconds
    speed_kmh = speed_mps * 3.6

    return speed_kmh <= max_kmh


def evaluate_reports(
    reports: Sequence[SightingReport],
    cluster_radius_m: float = settings.CONSENSUS_CLUSTER_RADIUS_METERS,
    confidence_threshold: float = settings.CONSENSUS_CONFIDENCE_THRESHOLD,
    min_reporters: int = settings.CONSENSUS_MIN_REPORTERS,
) -> ConsensusResult:
    """
    Evaluate a cluster of reports for a sculpture and decide if official state should transition.
    """
    if not reports:
        return ConsensusResult(
            decision=ConsensusDecision.INSUFFICIENT_EVIDENCE,
            confidence_score=0.0,
            distinct_reporters=0,
            centroid_latitude=0.0,
            centroid_longitude=0.0,
            consensus_status="unknown",
        )

    # Calculate centroid coordinates
    avg_lat = sum(r.latitude for r in reports) / len(reports)
    avg_lon = sum(r.longitude for r in reports) / len(reports)

    # Filter reports that fall within the cluster radius of the centroid
    valid_reports = [
        r
        for r in reports
        if haversine_distance_meters(avg_lat, avg_lon, r.latitude, r.longitude) <= cluster_radius_m
    ]

    distinct_reporters = len({r.reporter_id for r in valid_reports})
    total_confidence = sum(r.trust_score for r in valid_reports)

    # Find dominant status
    status_weights: dict[str, float] = {}
    for r in valid_reports:
        status_weights[r.reported_status] = (
            status_weights.get(r.reported_status, 0.0) + r.trust_score
        )

    dominant_status = (
        max(status_weights, key=lambda k: status_weights[k]) if status_weights else "unknown"
    )

    # Evaluate decision criteria
    if (
        total_confidence >= confidence_threshold
        and distinct_reporters >= min_reporters
        and status_weights.get(dominant_status, 0.0) >= (total_confidence * 0.75)
    ):
        decision = ConsensusDecision.AUTO_APPROVE
    elif total_confidence >= 1.5 or distinct_reporters >= 2:
        decision = ConsensusDecision.PENDING_MODERATION
    else:
        decision = ConsensusDecision.INSUFFICIENT_EVIDENCE

    return ConsensusResult(
        decision=decision,
        confidence_score=total_confidence,
        distinct_reporters=distinct_reporters,
        centroid_latitude=avg_lat,
        centroid_longitude=avg_lon,
        consensus_status=dominant_status,
    )


def adjust_trust_score(
    current_score: float,
    verified_positive: bool,
    boost: float = 0.05,
    penalty: float = 0.15,
) -> float:
    """
    Adjust a user's trust score based on report moderation outcome.
    Clamped between 0.0 and 1.0.
    """
    new_score = current_score + boost if verified_positive else current_score - penalty

    return max(0.0, min(1.0, round(new_score, 4)))
