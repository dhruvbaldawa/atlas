"""Tests for workflow API endpoints."""

import pytest
from fastapi.testclient import TestClient
from temporalio.testing import WorkflowEnvironment

from backend.api.schemas import WorkflowResponse


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


@pytest.mark.asyncio
async def test_health_check(client: TestClient, workflow_environment: WorkflowEnvironment):
    """Test the health check endpoint using a real in-memory Temporal environment.

    This test uses a real workflow environment instead of mocks to provide a more
    accurate test of the health check functionality.
    """
    # Given
    endpoint = "/health"

    # When
    response = client.get(endpoint)

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


def test_execute_dummy_workflow(client: TestClient):
    """Test the execution of a dummy workflow via API."""
    # Given
    endpoint = "/workflows/dummy"
    expected_workflow_id = "dummy-workflow-test"

    # When
    response = client.post(endpoint)

    # Then
    # Verify the response status and content
    assert response.status_code == 200
    workflow_response = WorkflowResponse(**response.json())
    assert workflow_response.workflow_id == expected_workflow_id
    assert workflow_response.status == "pending"

    # We can't verify the mock was called since we're using a real client
    # But we can verify the response was correct


def test_execute_dummy_workflow_with_message(client: TestClient):
    """Test the execution of a dummy workflow with a message via API."""
    # Given
    test_message = "Test Message"
    endpoint = f"/workflows/dummy?message={test_message}"
    expected_workflow_id = f"dummy-workflow-{test_message}"

    # When
    response = client.post(endpoint)

    # Then
    # Verify the response status and content
    assert response.status_code == 200
    workflow_response = WorkflowResponse(**response.json())
    assert workflow_response.workflow_id == expected_workflow_id
    assert workflow_response.status == "pending"

    # Since we're using the real client, we can't inspect call arguments
    # But we can verify the response includes the correct workflow ID that contains our message
