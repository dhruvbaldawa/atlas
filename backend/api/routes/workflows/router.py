"""Router for workflow-related endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from temporalio.client import Client

from backend.api.routes.core.dependencies import get_temporal_client
from backend.api.schemas import WorkflowResponse
from backend.temporal.client import start_workflow
from backend.workflows.dummy import DummyWorkflow

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(tags=["workflows"])

# Create a module level constant to avoid B008
temporal_client_dep = Depends(get_temporal_client)


@router.post("/dummy", response_model=WorkflowResponse)
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


@router.post("/dummy/sync", response_model=dict[str, Any])
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
