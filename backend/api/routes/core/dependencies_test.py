"""Tests for core dependencies."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException
from temporalio.client import Client

from backend.api.routes.core.dependencies import get_temporal_client


@pytest.mark.asyncio
async def test_get_temporal_client_success():
    """Test successful Temporal client connection."""
    # Mock successful client creation
    mock_client = AsyncMock(spec=Client)

    with patch(
        "backend.api.routes.core.dependencies.create_temporal_client", return_value=mock_client
    ) as mock_create_client:
        # When
        result = await get_temporal_client()

        # Then
        assert result == mock_client
        mock_create_client.assert_called_once()


@pytest.mark.asyncio
async def test_get_temporal_client_error():
    """Test error handling when Temporal client connection fails."""
    # Mock failed client creation
    test_error = Exception("Test connection error")

    with patch("backend.api.routes.core.dependencies.create_temporal_client", side_effect=test_error):
        # When/Then
        with pytest.raises(HTTPException) as excinfo:
            await get_temporal_client()

        # Verify the exception details
        assert excinfo.value.status_code == 503
        assert "Temporal service unavailable" in excinfo.value.detail
        assert excinfo.value.__cause__ == test_error
