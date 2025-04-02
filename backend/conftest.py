"""Test fixtures for the ATLAS project."""

from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment

from backend.api.main import app
from backend.db.connection import get_db_session

# We'll let pytest-asyncio manage the event_loop fixture automatically
# rather than providing our own implementation


@pytest_asyncio.fixture
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


@pytest_asyncio.fixture
async def test_db_session(test_db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session."""
    # Using async_sessionmaker instead of sessionmaker for async sessions
    async_session_factory = async_sessionmaker(bind=test_db_engine, expire_on_commit=False)
    async with async_session_factory() as session:
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
def client(override_get_db: None, temporal_client: Client) -> Generator[TestClient, None, None]:
    """Create a FastAPI test client with the in-memory Temporal client.

    This is the primary fixture for API tests that need both database and Temporal.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def workflow_environment() -> AsyncGenerator[WorkflowEnvironment, None]:
    """Create a Temporal workflow test environment using time-skipping.

    Time-skipping allows tests with timers and delays to run quickly.
    """
    env = await WorkflowEnvironment.start_time_skipping()
    yield env
    await env.shutdown()


@pytest_asyncio.fixture
async def temporal_client(workflow_environment: WorkflowEnvironment) -> AsyncGenerator[Client, None]:
    """Create a Temporal client for testing using the in-memory workflow environment.

    This is the primary fixture for getting a Temporal client for tests.
    """
    # Get the real Temporal client from the in-memory workflow environment
    client = workflow_environment.client

    # Override the app's dependency to use this real client for API tests
    from backend.api.main import get_temporal_client

    async def _get_real_temporal_client() -> Client:
        return client

    app.dependency_overrides[get_temporal_client] = _get_real_temporal_client
    yield client
    app.dependency_overrides.pop(get_temporal_client, None)
