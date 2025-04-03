"""Temporal client configuration for ATLAS.

This module provides utilities for creating and managing Temporal client connections,
including error handling and retry mechanisms.
"""

import logging
from functools import lru_cache
from typing import Any

from temporalio.client import Client

from backend.config import get_settings

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()


async def create_temporal_client(
    server_url: str | None = None,
    namespace: str | None = None,
) -> Client:
    """Create a Temporal client connection.

    Args:
        server_url: Optional server URL, defaults to value from settings
        namespace: Optional namespace, defaults to value from settings

    Returns:
        Client: Configured Temporal client

    Raises:
        Exception: If connection to Temporal server fails
    """
    # Use values from settings if not provided
    server_url = server_url or settings.temporal.get_server_url()
    namespace = namespace or settings.temporal.namespace

    logger.info(f"Connecting to Temporal server at {server_url}, namespace: {namespace}")

    try:
        # Connect to Temporal with simple configuration
        client = await Client.connect(
            server_url,
            namespace=namespace,
        )
        logger.info("Connected to Temporal server successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Temporal server: {e}")
        raise


@lru_cache
def get_workflow_id_prefix() -> str:
    """Get workflow ID prefix based on environment.

    Returns:
        str: Workflow ID prefix with environment
    """
    env = settings.env
    return f"atlas-{env}"


async def start_workflow(
    client: Client,
    workflow_type: Any,
    *args: Any,
    id_suffix: str = "",
    task_queue: str = "default",
    **kwargs: Any,
) -> str:
    """Start a workflow execution with proper ID prefixing.

    Args:
        client: Temporal client
        workflow_type: Workflow class or function
        id_suffix: Suffix to append to the workflow ID
        task_queue: Task queue to use for the workflow
        *args: Positional arguments to pass to the workflow
        **kwargs: Keyword arguments to pass to the workflow

    Returns:
        str: Workflow ID of the started workflow
    """
    workflow_id = f"{get_workflow_id_prefix()}-{workflow_type.__name__}"
    if id_suffix:
        workflow_id = f"{workflow_id}-{id_suffix}"

    logger.info(f"Starting workflow: {workflow_type.__name__} with ID: {workflow_id}")

    # Start the workflow but don't need to store the handle
    await client.start_workflow(
        workflow_type,
        *args,
        id=workflow_id,
        task_queue=task_queue,
        **kwargs,
    )

    logger.info(f"Workflow started: {workflow_id}")
    return workflow_id
