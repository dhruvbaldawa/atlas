"""Tests for Temporal client utilities."""

from unittest.mock import AsyncMock, patch

import pytest
from temporalio.client import Client

from backend.temporal.client import (
    create_temporal_client,
    get_workflow_id_prefix,
    start_workflow,
)


@pytest.mark.asyncio
async def test_create_temporal_client():
    """Test creating a Temporal client.

    Given: Mocked Client.connect method
    When: create_temporal_client is called
    Then: Client.connect should be called with correct parameters and
         the client should be returned
    """
    # Given
    mock_client = AsyncMock(spec=Client)

    # When/Then
    with patch("backend.temporal.client.Client.connect", return_value=mock_client) as mock_connect:
        # Call the function
        client = await create_temporal_client(server_url="test-url", namespace="test-ns")

        # Verify
        mock_connect.assert_called_once_with("test-url", namespace="test-ns")
        assert client == mock_client


@pytest.mark.asyncio
async def test_create_temporal_client_error():
    """Test error handling when creating a Temporal client.

    Given: Client.connect raises an exception
    When: create_temporal_client is called
    Then: The exception should be re-raised
    """
    # Given
    test_exception = ConnectionError("Test connection error")

    # When/Then
    with patch("backend.temporal.client.Client.connect", side_effect=test_exception) as mock_connect:
        with pytest.raises(ConnectionError, match="Test connection error"):
            await create_temporal_client(server_url="test-url", namespace="test-ns")

        # Verify
        mock_connect.assert_called_once_with("test-url", namespace="test-ns")


def test_get_workflow_id_prefix():
    """Test getting workflow ID prefix.

    Given: Mocked settings with a known environment
    When: get_workflow_id_prefix is called
    Then: A correctly formatted prefix should be returned
    """
    # Clear the lru_cache to ensure our mock is used
    get_workflow_id_prefix.cache_clear()

    # Given
    with patch("backend.temporal.client.settings") as mock_settings:
        mock_settings.env = "test"

        # When
        prefix = get_workflow_id_prefix()

        # Then
        assert prefix == "atlas-test"


@pytest.mark.asyncio
async def test_start_workflow():
    """Test starting a workflow.

    Given: A mock client and a workflow type
    When: start_workflow is called
    Then: client.start_workflow should be called with correct parameters
          and the workflow ID should be returned
    """
    # Given
    mock_client = AsyncMock(spec=Client)

    # Create a mock workflow class
    class TestWorkflow:
        __name__ = "TestWorkflow"

    # Mock the get_workflow_id_prefix function
    with patch("backend.temporal.client.get_workflow_id_prefix", return_value="atlas-test"):
        # When
        workflow_id = await start_workflow(
            client=mock_client,
            workflow_type=TestWorkflow,
            arg1="test",
            id_suffix="suffix",
            task_queue="test-queue",
            kwarg1="test",
        )

        # Then
        # Check that the workflow was started with the correct parameters
        mock_client.start_workflow.assert_called_once()
        call_args = mock_client.start_workflow.call_args

        # Check positional arguments
        assert call_args[0][0] == TestWorkflow

        # Check keyword arguments
        assert call_args[1]["id"] == "atlas-test-TestWorkflow-suffix"
        assert call_args[1]["task_queue"] == "test-queue"
        assert call_args[1]["arg1"] == "test"
        assert call_args[1]["kwarg1"] == "test"

        # Check returned workflow ID
        assert workflow_id == "atlas-test-TestWorkflow-suffix"


@pytest.mark.asyncio
async def test_start_workflow_no_suffix():
    """Test starting a workflow without an ID suffix.

    Given: A mock client and a workflow type
    When: start_workflow is called without an ID suffix
    Then: client.start_workflow should be called with a workflow ID
          that doesn't include a suffix
    """
    # Given
    mock_client = AsyncMock(spec=Client)

    # Create a mock workflow class
    class TestWorkflow:
        __name__ = "TestWorkflow"

    # Mock the get_workflow_id_prefix function
    with patch("backend.temporal.client.get_workflow_id_prefix", return_value="atlas-test"):
        # When
        workflow_id = await start_workflow(client=mock_client, workflow_type=TestWorkflow, task_queue="test-queue")

        # Then
        mock_client.start_workflow.assert_called_once_with(
            TestWorkflow, id="atlas-test-TestWorkflow", task_queue="test-queue"
        )
        assert workflow_id == "atlas-test-TestWorkflow"
