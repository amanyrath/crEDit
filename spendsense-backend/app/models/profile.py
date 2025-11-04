"""Profile model - User information and roles"""

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin, UpdatedTimestampMixin


class Profile(Base, UpdatedTimestampMixin):
    """User profile with role information"""

    __tablename__ = "profiles"

    user_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        comment="User ID from Cognito (UUID)",
    )
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address",
    )
    role = Column(
        String(20),
        nullable=False,
        comment="User role: 'consumer' or 'operator'",
    )

    # Relationships
    consent_records = relationship("ConsentRecord", back_populates="profile", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="profile", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="profile", cascade="all, delete-orphan")
    computed_features = relationship("ComputedFeature", back_populates="profile", cascade="all, delete-orphan")
    persona_assignments = relationship("PersonaAssignment", back_populates="profile", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="profile", cascade="all, delete-orphan")
    chat_logs = relationship("ChatLog", back_populates="profile", cascade="all, delete-orphan")
    operator_actions_as_operator = relationship(
        "OperatorAction",
        foreign_keys="OperatorAction.operator_id",
        back_populates="operator",
        cascade="all, delete-orphan",
    )
    operator_actions_as_user = relationship(
        "OperatorAction",
        foreign_keys="OperatorAction.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Profile(user_id={self.user_id}, email={self.email}, role={self.role})>"

