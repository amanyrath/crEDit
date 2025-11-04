"""Base model with common fields"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Mixin for created_at timestamp"""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the record was created",
    )


class UpdatedTimestampMixin(TimestampMixin):
    """Mixin for created_at and updated_at timestamps"""

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Timestamp when the record was last updated",
    )


def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid4())

