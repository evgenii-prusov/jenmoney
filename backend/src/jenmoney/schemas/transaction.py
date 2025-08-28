from datetime import datetime, date
from typing import Annotated

from pydantic import Field

from jenmoney.schemas.base import BaseAPIModel
from jenmoney.schemas.account import Currency


class TransactionBase(BaseAPIModel):
    """Base transaction model with core fields."""

    account_id: int
    amount: Annotated[
        float, Field(description="Transaction amount (positive for income, negative for expense)")
    ]
    description: str | None = None
    transaction_date: date = Field(default_factory=lambda: date.today())


class TransactionCreate(TransactionBase):
    """Model for creating a new transaction."""

    category_id: int | None = None


class TransactionUpdate(BaseAPIModel):
    """Model for updating a transaction."""

    amount: (
        Annotated[
            float,
            Field(description="Transaction amount (positive for income, negative for expense)"),
        ]
        | None
    ) = None
    category_id: int | None = None
    description: str | None = None
    transaction_date: date | None = None


class TransactionResponse(TransactionBase):
    """Model for transaction responses."""

    id: int
    currency: Currency
    category_id: int | None = None
    created_at: datetime
    updated_at: datetime


class TransactionListResponse(BaseAPIModel):
    """Paginated response for transaction listings."""

    items: list[TransactionResponse]
    total: int
    page: int = 1
    size: int = 10
    pages: int
