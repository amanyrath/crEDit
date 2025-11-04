"""Chat log model - Chat history with guardrails status"""

from sqlalchemy import Column, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class ChatLog(Base, TimestampMixin):
    """Chat log entry for AI chat interactions"""

    __tablename__ = "chat_logs"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique chat log ID",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID from profiles table",
    )
    message = Column(
        Text,
        nullable=False,
        comment="User's message",
    )
    response = Column(
        Text,
        nullable=False,
        comment="AI response",
    )
    guardrails_passed = Column(
        Boolean,
        server_default="true",
        nullable=False,
        comment="Whether guardrails validation passed",
    )

    # Relationships
    profile = relationship("Profile", back_populates="chat_logs")

    # Index for chronological queries
    __table_args__ = (
        # created_at is already indexed via TimestampMixin, but we can add explicit index if needed
    )

    def __repr__(self) -> str:
        return f"<ChatLog(id={self.id}, user_id={self.user_id}, guardrails_passed={self.guardrails_passed})>"

