from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.routers import auth, sculptures, users

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Digital ecosystem backend for Cali's public art (Novias del Gato).",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(sculptures.router)


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "env": settings.ENV,
    }
