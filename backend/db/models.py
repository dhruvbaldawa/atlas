"""Base models for ATLAS database entities.

This module provides base model classes with common fields and behaviors
for all database entities in the ATLAS system.
"""

from datetime import datetime

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import CHAR
from sqlmodel import Field, SQLModel
from ulid import new as new_ulid


def generate_ulid() -> str:
    """Generate a ULID string.

    Returns a lexicographically sortable unique identifier as a string.
    """
    return str(new_ulid())


class BaseModel(SQLModel):
    """Base model with common attributes for all database entities."""

    id: str = Field(
        sa_column=Column(
            CHAR(26),
            primary_key=True,
            default=generate_ulid,
            index=True,
        )
    )
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column("updated_at", nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True),
    )


class TimestampMixin(SQLModel):
    """Mixin for models that need timestamp tracking."""

    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column=Column("updated_at", nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True),
    )


class SoftDeleteMixin(SQLModel):
    """Mixin for models that support soft deletion."""

    deleted_at: datetime | None = Field(default=None, index=True)

    def soft_delete(self) -> None:
        """Mark the record as deleted without removing from database."""
        self.deleted_at = datetime.utcnow()
