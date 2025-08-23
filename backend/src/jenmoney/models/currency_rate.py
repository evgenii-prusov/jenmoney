from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Index, Integer, Numeric, String

from jenmoney.database import Base


class CurrencyRate(Base):  # type: ignore[misc, valid-type]
    __tablename__ = "currency_rates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    currency_from = Column(String(3), nullable=False)
    currency_to = Column(String(3), nullable=False, default="USD")
    rate = Column(
        Numeric(precision=19, scale=6),
        nullable=False,
    )
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)
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

    __table_args__ = (
        Index(
            "idx_currency_rate_lookup",
            "currency_from",
            "currency_to",
            "effective_from",
        ),
    )
