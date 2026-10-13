from fastapi import APIRouter
from app.config import settings
from app.schemas import HealthCheck

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheck)
def get_health() -> HealthCheck:
    """Health check endpoint to verify service availability."""
    return HealthCheck(
        status="ok",
        project=settings.PROJECT_NAME,
        version="0.1.0"
    )
