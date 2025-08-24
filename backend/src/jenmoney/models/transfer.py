from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Numeric, String, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from jenmoney.database import Base


class Transfer(Base):  # type: ignore[misc, valid-type]
    __tablename__ = "transfers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Source account information
    from_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    from_amount = Column(
        Numeric(precision=19, scale=2),
        nullable=False,
    )
    from_currency = Column(String(3), nullable=False)

    # Destination account information
    to_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    to_amount = Column(
        Numeric(precision=19, scale=2),
        nullable=False,
    )
    to_currency = Column(String(3), nullable=False)

    # Exchange rate used for conversion (if currencies differ)
    exchange_rate = Column(Numeric(precision=19, scale=8), nullable=True)

    # Optional description
    description = Column(Text, nullable=True)

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
    from_account = relationship("Account", foreign_keys=[from_account_id])
    to_account = relationship("Account", foreign_keys=[to_account_id])
