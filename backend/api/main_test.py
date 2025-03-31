"""Tests for the API module."""

from fastapi.testclient import TestClient


def test_root(client: TestClient) -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to ATLAS API"}
