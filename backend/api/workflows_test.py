"""Tests for workflow API endpoints."""

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment

from backend.api.main import WorkflowResponse


def test_root_endpoint(client: TestClient):
    """Test the root endpoint returns the welcome message."""
    # Given
    endpoint = "/"
    expected_message = {"message": "Welcome to ATLAS API"}

    # When
    response = client.get(endpoint)

    # Then
    assert response.status_code == 200
    assert response.json() == expected_message


@pytest.fixture
async def client_with_real_temporal(
    client: TestClient,
    temporal_client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> TestClient:
    """Create a test client that uses the real in-memory Temporal client."""
    async def _get_real_temporal_client() -> Client:
        return temporal_client

    # Override the Temporal client dependency to use our real in-memory client
    monkeypatch.setattr("backend.api.main.get_temporal_client", _get_real_temporal_client)
    return client


@pytest.mark.asyncio
async def test_health_check(client_with_real_temporal: TestClient, workflow_environment: WorkflowEnvironment):
    """Test the health check endpoint using a real in-memory Temporal environment.

    This test uses a real workflow environment instead of mocks to provide a more
    accurate test of the health check functionality.
    """
    # Given
    endpoint = "/health"

    # When
    response = client_with_real_temporal.get(endpoint)

    # Then
    assert response.status_code == 200

    # Get the actual response
    data = response.json()

    # Assert that we get a healthy state with a real temporal client
    assert data["status"] == "healthy"
    assert data["database"] is True
    assert data["temporal"] is True
    assert isinstance(data["version"], str)
    assert data["version"] != ""


def test_execute_dummy_workflow(client_with_mock_temporal: TestClient, mock_temporal_client: MagicMock):
    """Test the execution of a dummy workflow via API."""
    # Given
    endpoint = "/workflows/dummy"
    expected_workflow_id = "dummy-workflow-test"

    # When
    response = client_with_mock_temporal.post(endpoint)

    # Then
    # Verify the response status and content
    assert response.status_code == 200
    workflow_response = WorkflowResponse(**response.json())
    assert workflow_response.workflow_id == expected_workflow_id
    assert workflow_response.status == "pending"

    # Verify the mock was called correctly
    mock_temporal_client.start_workflow.assert_called_once()


def test_execute_dummy_workflow_with_message(client_with_mock_temporal: TestClient, mock_temporal_client: MagicMock):
    """Test the execution of a dummy workflow with a message via API."""
    # Given
    test_message = "Test Message"
    endpoint = f"/workflows/dummy?message={test_message}"
    expected_workflow_id = f"dummy-workflow-{test_message}"

    # When
    response = client_with_mock_temporal.post(endpoint)

    # Then
    # Verify the response status and content
    assert response.status_code == 200
    workflow_response = WorkflowResponse(**response.json())
    assert workflow_response.workflow_id == expected_workflow_id
    assert workflow_response.status == "pending"

    # Verify the mock was called with the message parameter
    call_args = mock_temporal_client.start_workflow.call_args
    assert call_args is not None

    # The message should be passed to the workflow
    args, kwargs = call_args
    assert test_message in str(args) or test_message in str(kwargs)
