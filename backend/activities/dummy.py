"""Dummy activities for testing Temporal integration.

This module provides simple activities that can be used to verify
that the Temporal integration is working properly.
"""

import logging
import time
from datetime import UTC, datetime

from temporalio import activity

logger = logging.getLogger(__name__)


@activity.defn
async def get_current_time() -> str:
    """Get the current time as a formatted string.

    This is a simple activity that returns the current time.
    It's useful for testing the Temporal workflow execution.

    Returns:
        str: Current time formatted as ISO string
    """
    logger.info("Executing get_current_time activity")
    return datetime.now(UTC).isoformat()


@activity.defn
async def echo_message(message: str) -> str:
    """Echo the provided message back.

    Args:
        message: Message to echo

    Returns:
        str: The same message
    """
    logger.info(f"Echoing message: {message}")
    return f"ECHO: {message}"


@activity.defn
async def simulate_work(duration_seconds: int = 2) -> str:
    """Simulate a long-running activity.

    Args:
        duration_seconds: Number of seconds to sleep

    Returns:
        str: Completion message
    """
    logger.info(f"Simulating work for {duration_seconds} seconds")

    # Note: Using time.sleep in an async function is generally not recommended
    # as it blocks the event loop. In a real-world scenario, you would use
    # asyncio.sleep instead. However, Temporal activities are executed in
    # their own context, so it's acceptable here.
    time.sleep(duration_seconds)

    logger.info("Work simulation complete")
    return f"Work completed after {duration_seconds} seconds"
