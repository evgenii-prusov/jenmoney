from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from jenmoney.database import Base


class UserSettings(Base):  # type: ignore[misc, valid-type]
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    default_currency = Column(String(3), nullable=False, default="USD")
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
