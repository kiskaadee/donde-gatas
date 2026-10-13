import asyncio
import math
import random
import uuid
from collections.abc import Sequence

from geoalchemy2.elements import WKTElement
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.session import AsyncSessionLocal
from api.db_models.sculpture import SculptureDB
from api.db_models.user import UserDB


def generate_normalized_embedding(seed_int: int, dimensions: int = 1280) -> list[float]:
    """
    Generate a deterministic, L2-normalized float vector simulating MobileNetV2 output.
    """
    rng = random.Random(seed_int)
    raw_vals = [rng.gauss(0.0, 1.0) for _ in range(dimensions)]
    magnitude = math.sqrt(sum(x * x for x in raw_vals))
    return [round(x / magnitude, 6) for x in raw_vals]


INITIAL_USER = {
    "id": uuid.UUID("123e4567-e89b-12d3-a456-426614174000"),
    "name": "Explorador Caleño",
    "email": "explorer@cali.gov.co",
    "trust_score": 0.85,
}

INITIAL_SCULPTURES = [
    {
        "id": uuid.UUID("234e5678-e89b-12d3-a456-426614174001"),
        "name": "La Novia Dulce",
        "artist": "Lorena Espitia",
        "year": 2006,
        "latitude": 3.450143,
        "longitude": -76.533282,
        "status": "on-site",
        "description": (
            "Decorated with sweets and candies representing Cali's culinary traditions. "
            "This bride is a homage to the traditional 'Macetas' given to godchildren every June."
        ),
        "unlocked_content": (
            "Cultural Oracle Insight: Lorena Espitia used bright fiberglass modeling to create a tactile sense "
            "of Colombian sugar candies. The sculpture is traditionally positioned near the river to evoke "
            "Cali's warm breeze carrying sweet aromas."
        ),
        "audio_url": "https://cdn.gatos.cali.gov.co/audio/novia_dulce.mp3",
        "embedding_seed": 101,
    },
    {
        "id": uuid.UUID("234e5678-e89b-12d3-a456-426614174002"),
        "name": "La Gata Ceremonial",
        "artist": "José Horacio Martínez",
        "year": 2006,
        "latitude": 3.451600,
        "longitude": -76.532600,
        "status": "moved",
        "description": (
            "A dark sculpture featuring intricate pre-Columbian gold patterns. "
            "It represents the ancestral heritage, jaguar spirits, and mythological elements of Southwest Colombia."
        ),
        "unlocked_content": (
            "Cultural Oracle Insight: The gold motifs are inspired by Calima culture gold artifacts. "
            "Its temporary relocation due to civic repairs on the Boulevard has triggered consensus recalculation, "
            "verifying its new spot 150m north."
        ),
        "audio_url": "https://cdn.gatos.cali.gov.co/audio/gata_ceremonial.mp3",
        "embedding_seed": 102,
    },
    {
        "id": uuid.UUID("234e5678-e89b-12d3-a456-426614174003"),
        "name": "La Gata Ilustrada",
        "artist": "Lucy Tejada",
        "year": 2006,
        "latitude": 3.450800,
        "longitude": -76.532900,
        "status": "on-site",
        "description": (
            "Covered in birds, trees, and dreamlike childhood imagery by Lucy Tejada, "
            "sister of master Hernando Tejada."
        ),
        "unlocked_content": (
            "Cultural Oracle Insight: Lucy Tejada painted this sculpture as a direct artistic dialogue "
            "with her brother's bronze cat, symbolizing Cali's natural biodiversity and poetic innocence."
        ),
        "audio_url": "https://cdn.gatos.cali.gov.co/audio/gata_ilustrada.mp3",
        "embedding_seed": 103,
    },
]


async def seed_data(session: AsyncSession) -> tuple[UserDB, Sequence[SculptureDB]]:
    """
    Idempotently seed the baseline user and cat sculptures into the database.
    """
    # 1. Seed user
    user = await session.get(UserDB, INITIAL_USER["id"])
    if not user:
        user = UserDB(
            id=INITIAL_USER["id"],
            name=INITIAL_USER["name"],
            email=INITIAL_USER["email"],
            trust_score=INITIAL_USER["trust_score"],
        )
        session.add(user)
    else:
        user.name = INITIAL_USER["name"]
        user.trust_score = INITIAL_USER["trust_score"]

    # 2. Seed sculptures
    seeded_sculptures: list[SculptureDB] = []
    for item in INITIAL_SCULPTURES:
        sculpture = await session.get(SculptureDB, item["id"])
        # PostGIS Point(Longitude Latitude) EPSG:4326
        point = WKTElement(f"POINT({item['longitude']} {item['latitude']})", srid=4326)
        embedding = generate_normalized_embedding(item["embedding_seed"])

        if not sculpture:
            sculpture = SculptureDB(
                id=item["id"],
                name=item["name"],
                artist=item["artist"],
                year=item["year"],
                description=item["description"],
                audio_url=item["audio_url"],
                unlocked_content=item["unlocked_content"],
                status=item["status"],
                location=point,
                embedding=embedding,
            )
            session.add(sculpture)
        else:
            sculpture.name = item["name"]
            sculpture.artist = item["artist"]
            sculpture.year = item["year"]
            sculpture.description = item["description"]
            sculpture.audio_url = item["audio_url"]
            sculpture.unlocked_content = item["unlocked_content"]
            sculpture.status = item["status"]
            sculpture.location = point
            sculpture.embedding = embedding

        seeded_sculptures.append(sculpture)

    await session.commit()
    return user, seeded_sculptures


async def run_seed() -> None:
    """CLI runner for database seeding."""
    print("🌱 Starting database seeding...")
    async with AsyncSessionLocal() as session:
        user, sculptures = await seed_data(session)
        print(f"✅ User seeded: {user.name} ({user.email})")
        for s in sculptures:
            print(f"✅ Sculpture seeded: {s.name} by {s.artist} [{s.status}]")
    print("🎉 Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(run_seed())
