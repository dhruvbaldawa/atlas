"""Tests for the dummy workflow using Temporal's testing framework."""

from inspect import signature

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from backend.activities.dummy import echo_message, get_current_time, simulate_work
from backend.workflows.dummy import DummyWorkflow


@pytest.mark.asyncio
async def test_dummy_workflow_structure():
    """Test basic structure and interface of the dummy workflow."""
    # Given
    # Instantiate the workflow class to examine its interface
    workflow = DummyWorkflow()

    # When/Then - This is a structural test where we're directly examining properties
    # Verify the workflow has the expected run method
    assert hasattr(workflow, "run")

    # Check the run method's signature accepts an optional message parameter
    sig = signature(workflow.run)
    assert len(sig.parameters) == 1
    assert "message" in sig.parameters
    assert sig.parameters["message"].default is None


@pytest.mark.asyncio
async def test_dummy_workflow_execution(workflow_environment: WorkflowEnvironment):
    """Test the dummy workflow execution using Temporal's test environment."""
    # Given
    # With pytest_asyncio.fixture, we directly get the environment
    env = workflow_environment
    # Create a worker with our workflow and activities
    async with Worker(
        env.client,
        task_queue="test-dummy-queue",
        workflows=[DummyWorkflow],
        activities=[get_current_time, echo_message, simulate_work],
    ):
        # When
        # Execute the workflow without a message
        result = await env.client.execute_workflow(
            DummyWorkflow.run,
            id="test-workflow-id",
            task_queue="test-dummy-queue",
        )

        # Then
        # Check the result structure
        assert isinstance(result, dict)
        assert "start_time" in result
        assert "echo_result" in result
        assert "work_result" in result
        assert "workflow_id" in result

        # Verify values - note we're not asserting exact values since they're real
        assert isinstance(result["start_time"], str)
        assert result["echo_result"] is None
        assert "Work completed after" in result["work_result"]
        assert result["workflow_id"] == "test-workflow-id"

        # Given (for the second test case - with message)
        test_message = "Hello, Temporal!"

        # When
        # Execute the workflow with a message
        result_with_message = await env.client.execute_workflow(
            DummyWorkflow.run,
            test_message,
            id="test-workflow-id-with-message",
            task_queue="test-dummy-queue",
        )

        # Then
        # Verify message handling
        assert result_with_message["echo_result"] == f"ECHO: {test_message}"


@pytest.mark.asyncio
async def test_dummy_workflow_replay(workflow_environment: WorkflowEnvironment):
    """Test workflow determinism through replay."""
    # Given
    test_message = "Replay Test"
    workflow_id = "replay-test-id"
    env = workflow_environment
    # Create worker and register workflow and activities
    async with Worker(
        env.client,
        task_queue="test-replay-queue",
        workflows=[DummyWorkflow],
        activities=[get_current_time, echo_message, simulate_work],
    ):
        # When
        # Execute the workflow first time
        await env.client.execute_workflow(
            DummyWorkflow.run,
            test_message,
            id=workflow_id,
            task_queue="test-replay-queue",
        )

        # Then
        # Get the workflow handle and verify it completed successfully
        handle = env.client.get_workflow_handle(workflow_id)
        result = await handle.result()

        # Verify we got a valid result
        assert isinstance(result, dict)
        assert result["echo_result"] == f"ECHO: {test_message}"
        # For a true replay test in a more complex scenario,
        # you would run another worker with the same workflow code
        # and ensure it produces the same result when replaying the same events
        # This is more relevant for workflows with complex logic and state
