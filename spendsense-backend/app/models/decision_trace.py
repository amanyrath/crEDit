"""Decision trace model - Full auditability logs"""

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class DecisionTrace(Base, TimestampMixin):
    """Decision trace for a recommendation (one-to-one with recommendation)"""

    __tablename__ = "decision_traces"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique decision trace ID",
    )
    recommendation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("recommendations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="Recommendation ID (one-to-one relationship)",
    )
    trace_data = Column(
        JSONB,
        nullable=False,
        comment="Complete decision trace JSON data",
    )

    # Relationships
    recommendation = relationship("Recommendation", back_populates="decision_trace")

    # Unique constraint (also enforced by unique=True on column, but explicit is better)
    __table_args__ = (
        UniqueConstraint("recommendation_id", name="uq_decision_traces_recommendation_id"),
    )

    def __repr__(self) -> str:
        return f"<DecisionTrace(id={self.id}, recommendation_id={self.recommendation_id})>"

