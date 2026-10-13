from fastapi import FastAPI
from app.config import settings
from app.routers import health

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Find gaming buddies by game, rank, playstyle, and schedule.",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Register routers
app.include_router(health.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "docs_url": "/docs",
        "health_check": "/health"
    }
