from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, DateTime, Numeric, String, Text, Integer

from jenmoney.database import Base


class Account(Base):  # type: ignore[misc]
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    currency = Column(String(3), nullable=False, default="EUR")
    balance = Column(
        Numeric(precision=19, scale=2),
        nullable=False,
        default=Decimal("0.00"),
    )
    description = Column(Text, nullable=True)
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
