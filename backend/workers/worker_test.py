"""Tests for Temporal worker implementation."""

import asyncio
from collections.abc import Callable
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from temporalio.client import Client
from temporalio.worker import Worker

from backend.workers.worker import (
    DEFAULT_TASK_QUEUE,
    discover_activities,
    discover_workflows,
    run_worker,
    shutdown_waiter,
)


@pytest.mark.asyncio
async def test_discover_workflows():
    """Test workflow discovery.

    Given: The workflow discovery function
    When: The function is called
    Then: It should return a list of workflow classes
    """
    # When
    workflows = await discover_workflows()

    # Then
    assert len(workflows) > 0
    # Verify we have the expected workflow types
    workflow_names = [w.__name__ for w in workflows]
    assert "DummyWorkflow" in workflow_names
    assert "ChainedDummyWorkflow" in workflow_names


@pytest.mark.asyncio
async def test_discover_activities():
    """Test activity discovery.

    Given: The activity discovery function
    When: The function is called
    Then: It should return a dictionary of activity functions
    """
    # When
    activities = await discover_activities()

    # Then
    assert len(activities) > 0
    # Verify we have the expected activity functions
    assert "get_current_time" in activities
    assert "echo_message" in activities
    assert "simulate_work" in activities


@pytest.mark.asyncio
async def test_run_worker():
    """Test worker initialization and running.

    Given: A mock Temporal client
    When: run_worker is called
    Then: A worker should be created with the correct parameters
          and run should be called on the worker
    """
    # Given
    mock_client = AsyncMock(spec=Client)
    mock_worker = AsyncMock(spec=Worker)

    # Create a return value for worker.run() that can be awaited
    run_coro = asyncio.sleep(0)
    mock_worker.run.return_value = run_coro

    # This function replaces asyncio.gather to avoid actually waiting
    async def mock_async_gather(*args: object) -> list[None]:
        # This allows the test to complete without waiting for the actual coroutines
        return [None for _ in args]

    # Patch all the necessary components
    with (
        patch("backend.workers.worker.Worker", return_value=mock_worker) as mock_worker_cls,
        patch("backend.workers.worker.asyncio.gather", side_effect=mock_async_gather) as mock_gather,
        patch("backend.workers.worker.shutdown_waiter") as mock_shutdown_waiter,
    ):
        # Make shutdown_waiter return a coroutine that completes immediately
        mock_shutdown_waiter.return_value = asyncio.sleep(0)

        # When - Call the function with our mock client
        await run_worker(mock_client)

        # Then - Verify Worker was constructed with the right parameters
        mock_worker_cls.assert_called_once()
        call_args = mock_worker_cls.call_args[0]
        assert call_args[0] == mock_client  # Client
        assert mock_worker_cls.call_args[1]["task_queue"] == DEFAULT_TASK_QUEUE

        # Verify worker.run was called
        mock_worker.run.assert_called_once()

        # Verify gather was called with the right arguments
        mock_gather.assert_called_once()
        # We don't compare the actual coroutine objects as they won't be equal
        assert len(mock_gather.call_args[0]) == 2  # Two arguments to gather


@pytest.mark.asyncio
async def test_shutdown_waiter():
    """Test graceful shutdown handler.

    Given: A mock worker and a shutdown event
    When: shutdown_waiter is called and the event is set
    Then: worker.shutdown() should be called
    """
    # Given
    mock_worker = AsyncMock(spec=Worker)
    shutdown_event = asyncio.Event()

    # Start the shutdown waiter in a task
    task = asyncio.create_task(shutdown_waiter(shutdown_event, mock_worker))

    # When - Trigger the shutdown
    shutdown_event.set()

    # Wait for the task to complete
    await task

    # Then - Verify worker.shutdown was called
    mock_worker.shutdown.assert_called_once()


@pytest.mark.asyncio
async def test_run_worker_with_signal_handling():
    """Test worker signal handling.

    Given: A mock worker and client
    When: A shutdown signal is simulated
    Then: The worker should be shut down gracefully
    """
    # Given
    mock_client = AsyncMock(spec=Client)
    mock_worker = AsyncMock(spec=Worker)

    # Mock signal handlers and event loop
    with (
        patch("backend.workers.worker.Worker", return_value=mock_worker),
        patch("backend.workers.worker.asyncio.get_event_loop") as mock_get_loop,
    ):
        # Create a mock event loop
        mock_loop = MagicMock()
        mock_get_loop.return_value = mock_loop

        # Set up a way to capture the signal handler
        signal_handlers = {}

        def mock_add_signal_handler(sig: int, callback: Callable[[], None]) -> None:
            signal_handlers[sig] = callback

        mock_loop.add_signal_handler.side_effect = mock_add_signal_handler

        # Make gather return immediately but allow us to capture its arguments
        gather_args = []

        async def mock_gather(*args: object) -> list[None]:
            gather_args.extend(args)
            # Simulate the first argument (worker.run) completing immediately
            return [None, None]

        with patch("backend.workers.worker.asyncio.gather", side_effect=mock_gather):
            # When - Run the worker
            await run_worker(mock_client)

            # Then - Verify signal handlers were registered
            assert mock_loop.add_signal_handler.call_count >= 2

            # Verify shutdown waiter was included in gather
            assert len(gather_args) == 2
            # The second argument should be the shutdown_waiter
            assert "shutdown_waiter" in str(gather_args[1])
