"""Core dependencies shared across API routes."""

import logging

from fastapi import HTTPException, status
from temporalio.client import Client

from backend.temporal.client import create_temporal_client

logger = logging.getLogger(__name__)


async def get_temporal_client() -> Client:
    """Get Temporal client connection.

    This is a shared dependency used by multiple route modules.
    """
    try:
        client = await create_temporal_client()
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Temporal: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Temporal service unavailable",
        ) from e
