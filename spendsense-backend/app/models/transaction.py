"""Transaction model - Transaction history"""

from sqlalchemy import Column, Date, ForeignKey, Index, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class Transaction(Base, TimestampMixin):
    """Transaction record"""

    __tablename__ = "transactions"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique transaction ID",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID from profiles table",
    )
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey("accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Account ID from accounts table",
    )
    date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Transaction date",
    )
    merchant = Column(
        String(255),
        nullable=False,
        comment="Merchant name",
    )
    amount = Column(
        Numeric(10, 2),
        nullable=False,
        comment="Transaction amount (negative for debits, positive for credits)",
    )
    category = Column(
        String(100),
        nullable=True,
        comment="Transaction category",
    )

    # Relationships
    profile = relationship("Profile", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")

    # Composite index for efficient querying
    __table_args__ = (
        Index("idx_transactions_user_date", "user_id", "date", postgresql_ops={"date": "DESC"}),
    )

    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, user_id={self.user_id}, merchant={self.merchant}, amount={self.amount}, date={self.date})>"

