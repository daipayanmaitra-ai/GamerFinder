from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.database import Base, engine
from app import models  # noqa: F401 - Register models with Base metadata
from app.seed import seed_games_and_ranks
from app.routers import health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Automatically create tables on startup
    Base.metadata.create_all(bind=engine)
    # Seed initial games (Valorant & PUBG) and their ordered rank tiers
    seed_games_and_ranks()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Find gaming buddies by game, rank, playstyle, and schedule.",
    version="0.1.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# Register routers
app.include_router(health.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs_url": "/docs",
        "health_check": "/health",
    }
