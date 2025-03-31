"""Main FastAPI application for ATLAS."""

from fastapi import FastAPI

app = FastAPI(
    title="ATLAS API",
    description="API for transforming web articles into valuable knowledge assets",
    version="0.1.0",
)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to ATLAS API"}
