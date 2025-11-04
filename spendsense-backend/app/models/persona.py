"""Persona assignment model - Persona tracking over time windows"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class PersonaAssignment(Base, TimestampMixin):
    """Persona assignment for a user in a time window"""

    __tablename__ = "persona_assignments"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique persona assignment ID",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID from profiles table",
    )
    time_window = Column(
        String(10),
        nullable=False,
        comment="Time window: '30d', '90d', or '180d'",
    )
    persona = Column(
        String(50),
        nullable=False,
        comment="Persona: 'high_utilization', 'subscription_heavy', 'variable_income_budgeter', 'savings_builder', 'general_wellness'",
    )
    assigned_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the persona was assigned",
    )

    # Relationships
    profile = relationship("Profile", back_populates="persona_assignments")

    # Composite index for efficient querying
    __table_args__ = (
        Index("idx_persona_assignments_user_window", "user_id", "time_window"),
    )

    def __repr__(self) -> str:
        return f"<PersonaAssignment(id={self.id}, user_id={self.user_id}, persona={self.persona}, time_window={self.time_window})>"

