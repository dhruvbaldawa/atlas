"""Main FastAPI application for ATLAS."""

import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from temporalio.client import Client

from backend.config import get_settings
from backend.db.connection import get_db_session, init_db
from backend.temporal.client import create_temporal_client, start_workflow
from backend.workflows.dummy import DummyWorkflow

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources during application lifecycle."""
    # Startup logic
    logger.info("Starting ATLAS API")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    # Give control back to FastAPI
    yield

    # Shutdown logic
    logger.info("Shutting down ATLAS API")


app = FastAPI(
    title="ATLAS API",
    description="API for transforming web articles into valuable knowledge assets",
    version="0.1.0",
    debug=settings.api.debug,
    lifespan=lifespan,
)


# Define response models
class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    database: bool
    temporal: bool


class WorkflowResponse(BaseModel):
    """Workflow execution response model."""

    workflow_id: str
    message: str
    status: str


# Define dependencies
async def get_temporal_client() -> Client:
    """Get Temporal client connection."""
    try:
        client = await create_temporal_client()
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Temporal: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Temporal service unavailable",
        ) from e


# Endpoints
@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to ATLAS API"}


# Create a module level constant to avoid B008
temporal_client_dep = Depends(get_temporal_client)


@app.get("/health", response_model=HealthResponse)
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

    return HealthResponse(
        status=overall_status,
        version=app.version,
        database=database_ok,
        temporal=temporal_ok,
    )


@app.post("/workflows/dummy", response_model=WorkflowResponse)
async def execute_dummy_workflow(
    background_tasks: BackgroundTasks,
    temporal_client: Client = temporal_client_dep,
    message: str | None = Query(None, description="Optional message to include in workflow"),
) -> WorkflowResponse:
    """Execute a dummy workflow asynchronously."""
    try:
        workflow_id = f"dummy-workflow-{message or 'test'}"

        # Start workflow in background
        background_tasks.add_task(
            start_workflow,
            temporal_client,
            DummyWorkflow.run,
            message,
            id_suffix=workflow_id,
            task_queue="atlas-default",
        )

        return WorkflowResponse(
            workflow_id=workflow_id,
            message="Workflow started asynchronously",
            status="pending",
        )
    except Exception as e:
        logger.error(f"Failed to start workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}",
        ) from e


@app.post("/workflows/dummy/sync", response_model=dict[str, Any])
async def execute_dummy_workflow_sync(
    temporal_client: Client = temporal_client_dep,
    message: str | None = Query(None, description="Optional message to include in workflow"),
) -> dict[str, Any]:
    """Execute a dummy workflow synchronously and wait for the result."""
    try:
        # Execute workflow and wait for result
        handle = await temporal_client.start_workflow(
            DummyWorkflow.run,
            message,
            id=f"dummy-sync-{message or 'test'}",
            task_queue="atlas-default",
        )

        # Wait for result (without explicit timeout since the SDK handles timeouts internally)
        result = await handle.result()
        return result
    except Exception as e:
        logger.error(f"Failed to execute workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute workflow: {str(e)}",
        ) from e
