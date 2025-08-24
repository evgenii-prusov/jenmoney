from datetime import datetime, timezone
import enum

from sqlalchemy import Column, DateTime, String, Text, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship

from jenmoney.database import Base


class CategoryType(enum.Enum):
    """Category type enumeration."""
    INCOME = "income"
    EXPENSE = "expense"


class Category(Base):  # type: ignore[misc, valid-type]
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    type = Column(Enum(CategoryType), nullable=False, index=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)
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

    # Self-referencing relationship
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")