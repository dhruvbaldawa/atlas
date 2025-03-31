"""Shared test fixtures and utilities for ATLAS tests."""

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the FastAPI application.

    Returns:
        TestClient: A test client for making requests to the API.
    """
    return TestClient(app)


@pytest.fixture
def sample_article_url() -> str:
    """Provide a sample article URL for testing.

    Returns:
        str: A sample article URL.
    """
    return "https://example.com/test-article"
