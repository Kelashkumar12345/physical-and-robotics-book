"""Health check endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter, status
from pydantic import BaseModel

from src.api.deps import VectorStoreDep, SettingsDep

router = APIRouter()


class DependencyStatus(BaseModel):
    """Status of external dependencies."""

    qdrant: str = "unknown"
    openai: str = "unknown"


class HealthStatus(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    dependencies: DependencyStatus


@router.get(
    "/health",
    response_model=HealthStatus,
    responses={
        200: {"description": "Healthy"},
        503: {"description": "Unhealthy"},
    },
)
async def health_check(
    vector_store: VectorStoreDep,
    settings: SettingsDep,
) -> HealthStatus:
    """Check API health and dependencies."""
    dependencies = DependencyStatus()

    # Check Qdrant
    try:
        await vector_store.health_check()
        dependencies.qdrant = "up"
    except Exception:
        dependencies.qdrant = "down"

    # Check OpenAI (just verify key is configured)
    if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
        dependencies.openai = "up"
    else:
        dependencies.openai = "down"

    # Determine overall status
    all_up = dependencies.qdrant == "up" and dependencies.openai == "up"
    any_up = dependencies.qdrant == "up" or dependencies.openai == "up"

    if all_up:
        overall_status = "healthy"
    elif any_up:
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.now(timezone.utc).isoformat(),
        dependencies=dependencies,
    )
