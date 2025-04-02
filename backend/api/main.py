"""Main FastAPI application for ATLAS."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routes.health.router import router as health_router
from backend.api.routes.workflows.router import router as workflows_router
from backend.config import get_settings
from backend.db.connection import init_db

logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources during application lifecycle."""
    # Startup logic
    logger.info("Starting ATLAS API")

    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

    # Give control back to FastAPI
    yield

    # Shutdown logic
    logger.info("Shutting down ATLAS API")


app = FastAPI(
    title="ATLAS API",
    description="API for transforming web articles into valuable knowledge assets",
    version="0.1.0",
    debug=settings.api.debug,
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to ATLAS API"}


# Register routers
app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(workflows_router, prefix="/workflows", tags=["workflows"])
