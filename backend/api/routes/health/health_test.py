"""Tests for health endpoints."""

import pytest
from fastapi.testclient import TestClient
from temporalio.testing import WorkflowEnvironment


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
