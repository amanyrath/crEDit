"""Recommendation model - Generated recommendations"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class Recommendation(Base, TimestampMixin):
    """Recommendation for a user (education or offer)"""

    __tablename__ = "recommendations"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique recommendation ID",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID from profiles table",
    )
    type = Column(
        String(20),
        nullable=False,
        comment="Recommendation type: 'education' or 'offer'",
    )
    title = Column(
        String(255),
        nullable=False,
        comment="Recommendation title",
    )
    rationale = Column(
        Text,
        nullable=False,
        comment="Explanation of why this recommendation is shown",
    )
    shown_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Timestamp when recommendation was shown to user",
    )
    clicked = Column(
        Boolean,
        server_default="false",
        nullable=False,
        comment="Whether the user clicked on this recommendation",
    )

    # Relationships
    profile = relationship("Profile", back_populates="recommendations")
    decision_trace = relationship("DecisionTrace", back_populates="recommendation", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Recommendation(id={self.id}, user_id={self.user_id}, type={self.type}, title={self.title})>"

