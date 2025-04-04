"""Temporal worker implementation for ATLAS.

This module provides worker configuration and registration for Temporal
workflows and activities. It handles graceful shutdown and logging.
"""

import asyncio
import importlib
import inspect
import logging
import pkgutil
import signal
from collections.abc import Callable
from typing import Any

from temporalio.client import Client
from temporalio.worker import Worker

from backend.config import get_settings
from backend.temporal.client import create_temporal_client

logger = logging.getLogger(__name__)
settings = get_settings()

# Default task queue
DEFAULT_TASK_QUEUE = "atlas-default"


async def discover_workflows() -> list[Any]:
    """Discover workflow classes dynamically from the workflows package.

    Returns:
        List[Any]: List of workflow classes
    """
    import backend.workflows

    workflow_classes = []

    # Get all modules in the workflows package
    for _, module_name, _ in pkgutil.iter_modules(backend.workflows.__path__, backend.workflows.__name__ + "."):
        try:
            # Import the module
            module = importlib.import_module(module_name)

            # Find all classes in the module that have the @workflow.defn decorator
            for _, obj in inspect.getmembers(module, inspect.isclass):
                # Check if this is a workflow class
                if hasattr(obj, "__temporal_workflow_definition"):
                    workflow_classes.append(obj)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Error importing module {module_name}: {e}")

    logger.info(f"Discovered {len(workflow_classes)} workflow classes")
    return workflow_classes


async def discover_activities() -> dict[str, Callable]:
    """Discover activity functions dynamically from the activities package.

    Returns:
        Dict[str, Callable]: Dictionary of activity functions
    """
    import backend.activities

    activities = {}

    # Get all modules in the activities package
    for _, module_name, _ in pkgutil.iter_modules(backend.activities.__path__, backend.activities.__name__ + "."):
        try:
            # Import the module
            module = importlib.import_module(module_name)

            # Find all functions in the module that have the @activity.defn decorator
            for name, obj in inspect.getmembers(module, inspect.isfunction):
                # Check if this is an activity function (decorated with @activity.defn)
                if hasattr(obj, "__temporal_activity_definition"):
                    activities[name] = obj
        except (ImportError, AttributeError) as e:
            logger.warning(f"Error importing module {module_name}: {e}")

    logger.info(f"Discovered {len(activities)} activity functions")
    return activities


async def run_worker(
    client: Client,
    task_queue: str = DEFAULT_TASK_QUEUE,
) -> None:
    """Run a Temporal worker.

    Args:
        client: Temporal client
        task_queue: Task queue to listen on
    """
    logger.info(f"Starting worker on task queue: {task_queue}")

    # Discover workflows and activities
    workflows = await discover_workflows()
    activities = await discover_activities()

    # Create worker
    worker = Worker(
        client,
        task_queue=task_queue,
        workflows=workflows,
        activities=list(activities.values()),
    )

    # Handle graceful shutdown
    shutdown_event = asyncio.Event()

    def handle_signal(sig: Any) -> None:
        logger.info(f"Received signal {sig}, shutting down worker gracefully")
        shutdown_event.set()

    # Register signal handlers
    for sig in (signal.SIGINT, signal.SIGTERM):
        # Use a function factory to capture the loop variable properly
        def create_handler(s: int):
            return lambda: handle_signal(s)

        asyncio.get_event_loop().add_signal_handler(sig, create_handler(sig))

    # Run worker until shutdown is requested
    await asyncio.gather(
        worker.run(),
        shutdown_waiter(shutdown_event, worker),
    )


async def shutdown_waiter(shutdown_event: asyncio.Event, worker: Worker) -> None:
    """Wait for shutdown signal and gracefully shut down worker.

    Args:
        shutdown_event: Event that signals shutdown
        worker: Worker to shut down
    """
    await shutdown_event.wait()
    logger.info("Shutting down worker")
    await worker.shutdown()
    logger.info("Worker shutdown complete")


async def run_all_workers() -> None:
    """Run all workers needed for the application."""
    # Create Temporal client
    client = await create_temporal_client()

    # Run worker on default task queue
    await run_worker(client, DEFAULT_TASK_QUEUE)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Run worker
    asyncio.run(run_all_workers())
