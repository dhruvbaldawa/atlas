"""Tests for the API module."""

from fastapi.testclient import TestClient

from backend.api.main import app

client = TestClient(app)


def test_root() -> None:
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to ATLAS API"}


def test_prospecting() -> None:
    """Test the prospecting endpoint."""
    response = client.post(
        "/prospecting/",
        json={"url": "https://example.com", "purpose_tag": "research"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "status": "received",
        "url": "https://example.com",
        "purpose_tag": "research",
    }
