from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Numeric, String, Text, Integer, ForeignKey, Date
from sqlalchemy.orm import relationship

from jenmoney.database import Base


class Transaction(Base):  # type: ignore[misc, valid-type]
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Account relationship (single account for transaction)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)

    # Transaction amount (positive for income, negative for expense)
    amount = Column(
        Numeric(precision=19, scale=2),
        nullable=False,
    )

    # Currency (derived from account)
    currency = Column(String(3), nullable=False)

    # Optional category relationship
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)

    # Optional description
    description = Column(Text, nullable=True)

    # Transaction date (defaults to current date)
    transaction_date = Column(Date, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    account = relationship("Account", foreign_keys=[account_id])
    category = relationship("Category", foreign_keys=[category_id])
