"""Tests for dummy activities using Temporal's testing framework."""

# No longer need AsyncGenerator since we're using direct WorkflowEnvironment
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from backend.activities.dummy import echo_message, get_current_time, simulate_work


@pytest.mark.asyncio
async def test_get_current_time_direct():
    """Test the get_current_time activity directly without Temporal framework."""
    # Given
    now = datetime.now(UTC)

    # When
    result = await get_current_time()

    # Then
    # Verify it's a proper ISO format string
    assert isinstance(result, str)

    # Parse the result to ensure it's a valid datetime
    result_dt = datetime.fromisoformat(result)

    # The result should be very close to the current time
    assert now - timedelta(seconds=1) <= result_dt <= now + timedelta(seconds=1)


@pytest.mark.asyncio
async def test_echo_message_direct():
    """Test the echo_message activity directly without Temporal framework."""
    # Given
    test_message = "Hello, Temporal!"

    # When
    result = await echo_message(test_message)

    # Then
    # Verify the result includes the original message
    assert result == f"ECHO: {test_message}"

    # Test with an empty message
    # Given
    empty_message = ""

    # When
    empty_result = await echo_message(empty_message)

    # Then
    assert empty_result == "ECHO: "


@pytest.mark.asyncio
async def test_simulate_work_direct():
    """Test the simulate_work activity with timing verification."""
    # Given
    duration = 1  # Use a short duration for testing

    # When
    with patch("time.sleep") as mock_sleep:
        result = await simulate_work(duration)

    # Then
    # Verify the sleep was called with the right duration
    mock_sleep.assert_called_once_with(duration)

    # Verify the result message
    assert result == f"Work completed after {duration} seconds"


@pytest.mark.asyncio
async def test_simulate_work_with_default_direct():
    """Test simulate_work activity with default duration."""
    # Given
    expected_default_duration = 2  # seconds

    # When
    # Patch time.sleep to avoid waiting
    with patch("time.sleep") as mock_sleep:
        result = await simulate_work()

        # Then
        # Verify default duration was used (2 seconds)
        mock_sleep.assert_called_once_with(expected_default_duration)

        # Check the result message
        assert result == f"Work completed after {expected_default_duration} seconds"


@pytest.mark.asyncio
async def test_workflow_integration(workflow_environment: WorkflowEnvironment):
    """Integration test for workflow execution with real activities.

    This test demonstrates using Temporal's testing framework to verify
    the integration between workflows and activities without mocking.
    """
    # Given
    # Import the workflow here to avoid circular import issues
    from backend.workflows.dummy import DummyWorkflow

    test_message = "Integration Test Message"
    # With pytest_asyncio.fixture, we directly get the environment
    env = workflow_environment

    # Create a worker with our workflow and activities
    async with Worker(
        env.client,
        task_queue="test-integration-queue",
        workflows=[DummyWorkflow],
        activities=[get_current_time, echo_message, simulate_work],
    ):
        # When
        # Run the workflow with the integrated activities
        result = await env.client.execute_workflow(
            DummyWorkflow.run,
            test_message,
            id="test-integration-workflow",
            task_queue="test-integration-queue",
        )

        # Then
        # Verify basic structure and content
        assert isinstance(result, dict)
        assert "start_time" in result
        assert "echo_result" in result
        assert "work_result" in result
        assert "workflow_id" in result

        # Verify the echo message is correctly processed
        assert result["echo_result"] == f"ECHO: {test_message}"
