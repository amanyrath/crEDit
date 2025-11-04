"""Operator action model - Operator audit log"""

from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class OperatorAction(Base, TimestampMixin):
    """Operator action (override, flag, etc.)"""

    __tablename__ = "operator_actions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique operator action ID",
    )
    operator_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Operator user ID from profiles table",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Target user ID from profiles table",
    )
    action_type = Column(
        String(20),
        nullable=False,
        comment="Action type: 'override' or 'flag'",
    )
    reason = Column(
        Text,
        nullable=False,
        comment="Reason for the action",
    )

    # Relationships
    operator = relationship("Profile", foreign_keys=[operator_id], back_populates="operator_actions_as_operator")
    user = relationship("Profile", foreign_keys=[user_id], back_populates="operator_actions_as_user")

    def __repr__(self) -> str:
        return f"<OperatorAction(id={self.id}, operator_id={self.operator_id}, user_id={self.user_id}, action_type={self.action_type})>"

