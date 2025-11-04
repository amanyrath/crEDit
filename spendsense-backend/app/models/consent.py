"""Consent record model - Consent audit trail"""

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class ConsentRecord(Base, TimestampMixin):
    """Consent record for user data processing consent"""

    __tablename__ = "consent_records"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique consent record ID",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID from profiles table",
    )
    granted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when consent was granted",
    )
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when consent was revoked",
    )
    version = Column(
        String(10),
        server_default="1.0",
        nullable=False,
        comment="Consent version (e.g., '1.0')",
    )
    ip_address = Column(
        String(45),
        nullable=True,
        comment="IP address when consent was granted/revoked",
    )

    # Relationships
    profile = relationship("Profile", back_populates="consent_records")

    def __repr__(self) -> str:
        return f"<ConsentRecord(id={self.id}, user_id={self.user_id}, granted_at={self.granted_at})>"

