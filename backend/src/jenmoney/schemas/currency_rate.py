from datetime import datetime
from typing import Annotated

from pydantic import Field

from jenmoney.schemas.account import Currency
from jenmoney.schemas.base import BaseAPIModel


class CurrencyRateBase(BaseAPIModel):
    """Base currency rate model with core fields."""

    currency_from: Currency
    currency_to: Currency = Currency.USD
    rate: Annotated[float, Field(gt=0)]


class CurrencyRateCreate(CurrencyRateBase):
    """Model for creating a new currency rate."""

    effective_from: datetime
    effective_to: datetime | None = None


class CurrencyRateUpdate(BaseAPIModel):
    """Model for updating a currency rate."""

    rate: Annotated[float, Field(gt=0)] | None = None
    effective_to: datetime | None = None


class CurrencyRateResponse(CurrencyRateBase):
    """Model for currency rate responses."""

    id: int
    effective_from: datetime
    effective_to: datetime | None
    created_at: datetime
    updated_at: datetime


class CurrencyRateImport(BaseAPIModel):
    """Model for importing currency rates from CSV/JSON."""

    currency_from: Currency
    rate_to_usd: Annotated[float, Field(gt=0)]
    effective_from: datetime
    effective_to: datetime | None = None
