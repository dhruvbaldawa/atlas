"""Pydantic schema models for API endpoints."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    database: bool
    temporal: bool


class WorkflowResponse(BaseModel):
    """Workflow execution response model."""

    workflow_id: str
    message: str
    status: str
