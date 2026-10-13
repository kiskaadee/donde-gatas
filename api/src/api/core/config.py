from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    ENV: str = "development"
    PROJECT_NAME: str = "Novias del Gato API"
    VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/novias_db"

    # JWT
    JWT_SECRET: str = "insecure_dev_secret_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # OAuth / SSO
    GOOGLE_CLIENT_ID: str | None = None
    GOOGLE_CLIENT_SECRET: str | None = None
    GOOGLE_REDIRECT_URI: str | None = None

    # Recognition and Spatial Rules
    SIMILARITY_THRESHOLD: float = 0.65
    PROXIMITY_RADIUS_METERS: float = 15.0

    # Consensus Engine Thresholds
    CONSENSUS_CLUSTER_RADIUS_METERS: float = 20.0
    CONSENSUS_CONFIDENCE_THRESHOLD: float = 3.0
    CONSENSUS_MIN_REPORTERS: int = 3
    MAX_PLAUSIBLE_VELOCITY_KMH: float = 120.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
