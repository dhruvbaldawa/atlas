"""Database connection management for ATLAS.

This module provides utilities for creating and managing database connections
using SQLModel with async support.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel

from backend.config import get_settings

logger = logging.getLogger(__name__)

# Get database settings
settings = get_settings()

# Create async engine
engine = create_async_engine(
    settings.database.get_postgres_uri(),
    echo=settings.api.debug,
    future=True,
    pool_pre_ping=True,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session as an async context manager.

    Yields:
        AsyncSession: SQLAlchemy async session

    Example:
        ```python
        async with get_db_session() as session:
            result = await session.execute(select(Model))
            await session.commit()
        ```
    """
    session = async_session_factory()
    try:
        yield session
    except Exception as e:
        logger.error(f"Database session error: {e}")
        await session.rollback()
        raise
    finally:
        await session.close()


async def init_db() -> None:
    """Initialize database by creating all tables.

    This function should be called during application startup.
    It ensures all SQLModel models are created in the database.
    """
    async with engine.begin() as conn:
        # Import all models to ensure they're registered with SQLModel
        # before creating tables
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database initialized successfully")


async def close_db_connection() -> None:
    """Close database connection.

    This function should be called during application shutdown.
    """
    await engine.dispose()
    logger.info("Database connection closed")
