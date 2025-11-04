"""Account model - Synthetic bank accounts"""

from sqlalchemy import Column, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base, TimestampMixin


class Account(Base, TimestampMixin):
    """Bank account information"""

    __tablename__ = "accounts"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=func.gen_random_uuid(),
        comment="Unique account ID",
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="User ID from profiles table",
    )
    account_type = Column(
        String(30),
        nullable=False,
        comment="Account type: 'checking', 'savings', 'high_yield_savings', 'credit_card'",
    )
    account_number_last4 = Column(
        String(4),
        nullable=True,
        comment="Last 4 digits of account number",
    )
    balance = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Current account balance (negative for credit cards with debt)",
    )
    limit = Column(
        Numeric(10, 2),
        nullable=True,
        comment="Credit limit (for credit cards only)",
    )

    # Relationships
    profile = relationship("Profile", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, user_id={self.user_id}, account_type={self.account_type}, balance={self.balance})>"

