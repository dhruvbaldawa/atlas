"""Test fixtures for the ATLAS project."""

import asyncio
from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment

from backend.api.main import app
from backend.db.connection import get_db_session


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for testing async code."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_db_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Create a test database engine."""
    # Use in-memory SQLite for tests
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def test_db_session(test_db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    async_session = sessionmaker(bind=test_db_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
def override_get_db(test_db_session: AsyncSession) -> Generator[None, None, None]:
    """Override the get_db dependency."""

    async def _get_db_session() -> AsyncGenerator[AsyncSession, None]:
        yield test_db_session

    app.dependency_overrides[get_db_session] = _get_db_session
    yield
    app.dependency_overrides.pop(get_db_session, None)


@pytest.fixture
def client(override_get_db: None) -> Generator[TestClient, None, None]:
    """Create a FastAPI test client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def mock_temporal_client() -> AsyncGenerator[MagicMock, None]:
    """Create a mock Temporal client."""
    client_mock = AsyncMock(spec=Client)
    yield client_mock


@pytest.fixture
def override_get_temporal_client(
    mock_temporal_client: MagicMock,
) -> Generator[None, None, None]:
    """Override the get_temporal_client dependency."""
    from backend.api.main import get_temporal_client

    async def _get_mock_client() -> Client:
        return mock_temporal_client

    app.dependency_overrides[get_temporal_client] = _get_mock_client
    yield
    app.dependency_overrides.pop(get_temporal_client, None)


@pytest.fixture
def client_with_mock_temporal(
    override_get_db: None, override_get_temporal_client: None
) -> Generator[TestClient, None, None]:
    """Create a FastAPI test client with mocked Temporal client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
async def workflow_environment() -> AsyncGenerator[WorkflowEnvironment, None]:
    """Create a Temporal workflow test environment."""
    env = await WorkflowEnvironment.start_local()
    yield env
    await env.shutdown()


@pytest.fixture
async def temporal_client(workflow_environment: WorkflowEnvironment) -> AsyncGenerator[Client, None]:
    """Create a Temporal client for testing."""
    yield workflow_environment.client
