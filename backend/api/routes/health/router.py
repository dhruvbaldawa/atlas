"""Router for health-related endpoints."""

import logging

from fastapi import APIRouter, Depends
from temporalio.client import Client

from backend.api.routes.core.dependencies import get_temporal_client
from backend.api.schemas import HealthResponse
from backend.db.connection import get_db_session

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["health"])

# Create a module level constant to avoid B008
temporal_client_dep = Depends(get_temporal_client)


@router.get("/", response_model=HealthResponse)
async def health_check(
    temporal_client: Client = temporal_client_dep,
) -> HealthResponse:
    """Health check endpoint.

    Verifies connectivity to all services.
    """
    database_ok = True
    temporal_ok = True

    # Check database connection
    try:
        async with get_db_session() as _:
            pass
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        database_ok = False

    # Check Temporal connection
    try:
        # Check Temporal service client health directly
        # This is more reliable than trying to access a specific workflow
        await temporal_client.service_client.check_health()
        # If we get here, Temporal is connected
    except Exception as e:
        logger.error(f"Temporal health check failed: {e}")
        temporal_ok = False

    overall_status = "healthy" if database_ok and temporal_ok else "unhealthy"

    # Get version from app
    from backend.api.main import app

    return HealthResponse(
        status=overall_status,
        version=app.version,
        database=database_ok,
        temporal=temporal_ok,
    )
