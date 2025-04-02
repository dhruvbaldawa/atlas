"""Tests for health endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from temporalio.client import Client
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


@pytest.mark.asyncio
async def test_health_check_database_error(client: TestClient, monkeypatch: pytest.MonkeyPatch):
    """Test health check when database connection fails."""

    # Given a database error
    async def mock_db_session_error():
        class FailedSessionManager:
            async def __aenter__(self):
                raise Exception("Database connection error")

            async def __aexit__(self, exc_type: type, exc_val: Exception, exc_tb: object):
                pass

        return FailedSessionManager()

    # Apply the patch only within this test
    with patch("backend.api.routes.health.router.get_db_session", side_effect=mock_db_session_error):
        # When
        response = client.get("/health")

        # Then
        assert response.status_code == 200  # Still returns 200 even with errors
        data = response.json()

        # Should report database as down
        assert data["database"] is False
        assert data["status"] == "unhealthy"  # Overall status should be unhealthy


@pytest.mark.asyncio
async def test_health_check_temporal_error():
    """Test health check function directly when Temporal connection fails."""
    # Import the health_check function directly
    from backend.api.main import app
    from backend.api.routes.health.router import health_check

    # Create a mock Temporal client that raises an exception on check_health
    mock_client = AsyncMock(spec=Client)
    mock_service_client = AsyncMock()
    mock_service_client.check_health.side_effect = Exception("Temporal connection error")
    mock_client.service_client = mock_service_client

    # Call the health check function directly with our mock client
    response = await health_check(mock_client)

    # Verify the response
    assert response.status == "unhealthy"
    assert response.database is True  # Database should still be up
    assert response.temporal is False  # Temporal should be reported as down
    assert response.version == app.version
