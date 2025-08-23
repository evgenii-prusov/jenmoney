from datetime import datetime
from enum import Enum
from typing import Annotated

from pydantic import Field

from jenmoney.schemas.base import BaseAPIModel


class Currency(str, Enum):
    EUR = "EUR"
    USD = "USD"
    RUB = "RUB"
    JPY = "JPY"


class AccountBase(BaseAPIModel):
    """Base account model with core fields that are always present."""

    name: Annotated[str, Field(min_length=1, max_length=100)]
    currency: Currency = Currency.EUR


class AccountCreate(AccountBase):
    """Model for creating a new account. All fields from base are required."""

    balance: Annotated[float, Field(ge=0)] = 0.0
    description: str | None = None


class AccountUpdate(BaseAPIModel):
    """Model for updating an account. All fields are optional."""

    name: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    currency: Currency | None = None
    balance: Annotated[float, Field(ge=0)] | None = None
    description: str | None = None


class AccountResponse(AccountBase):
    """Model for account responses. Includes all fields plus metadata."""

    id: int
    balance: float
    percentage_of_total: float | None = None
    balance_in_default_currency: float | None = None
    default_currency: Currency | None = None
    exchange_rate_used: float | None = None
    description: str | None = None
    created_at: datetime
    updated_at: datetime


class AccountInDB(AccountResponse):
    """Internal model with all database fields."""

    pass


class AccountListResponse(BaseAPIModel):
    """Paginated response for account listings."""

    items: list[AccountResponse]
    total: int
    page: int = 1
    size: int = 10
    pages: int


class TotalBalanceResponse(BaseAPIModel):
    """Response for total balance calculation."""

    total_balance: float
    default_currency: Currency
    currency_breakdown: dict[str, float]
