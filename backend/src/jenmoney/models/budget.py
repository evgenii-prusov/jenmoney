from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, DateTime, Numeric, Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from jenmoney.database import Base


class Budget(Base):  # type: ignore[misc, valid-type]
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Budget period (year and month)
    budget_year = Column(Integer, nullable=False, index=True)
    budget_month = Column(Integer, nullable=False, index=True)

    # Category this budget applies to (only expense categories)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)

    # Planned amount for this category in this month
    planned_amount = Column(Numeric(precision=19, scale=2), nullable=False, default=Decimal("0.00"))

    # Currency (defaults to USD, can be set to user's preferred currency)
    currency = Column(String(3), nullable=False, default="USD")

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
    category = relationship("Category", foreign_keys=[category_id])

    # Unique constraint: one budget per category per month
    __table_args__ = (
        UniqueConstraint(
            "budget_year", "budget_month", "category_id", name="_budget_period_category_uc"
        ),
    )
