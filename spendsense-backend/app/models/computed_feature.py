"""Computed feature model - Cached behavioral signals"""

from sqlalchemy import Column, DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class ComputedFeature(Base, TimestampMixin):
    """Computed behavioral signal for a user"""

    __tablename__ = "computed_features"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique computed feature ID",
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
    signal_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Signal type: 'subscription', 'credit_utilization_*', 'savings_behavior', 'income_stability'",
    )
    signal_value = Column(
        JSONB,
        nullable=False,
        comment="Computed signal data as JSON",
    )
    computed_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Timestamp when the feature was computed",
    )

    # Relationships
    profile = relationship("Profile", back_populates="computed_features")

    # Composite index for efficient querying
    __table_args__ = (
        Index("idx_computed_features_user_window", "user_id", "time_window"),
    )

    def __repr__(self) -> str:
        return f"<ComputedFeature(id={self.id}, user_id={self.user_id}, signal_type={self.signal_type}, time_window={self.time_window})>"

