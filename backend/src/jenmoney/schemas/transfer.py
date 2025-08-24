from datetime import datetime
from typing import Annotated, Any

from pydantic import Field, model_validator

from jenmoney.schemas.base import BaseAPIModel
from jenmoney.schemas.account import Currency


class TransferBase(BaseAPIModel):
    """Base transfer model with core fields."""

    from_account_id: int
    to_account_id: int
    from_amount: Annotated[float, Field(gt=0)]
    description: str | None = None

    @model_validator(mode="before")
    @classmethod
    def validate_different_accounts(cls, values: Any) -> Any:
        """Ensure transfer is between different accounts."""
        if isinstance(values, dict):
            from_account_id = values.get("from_account_id")
            to_account_id = values.get("to_account_id")

            if from_account_id == to_account_id:
                raise ValueError("Transfer must be between different accounts")

        return values


class TransferCreate(TransferBase):
    """Model for creating a new transfer."""

    # Optional: specify destination amount for multi-currency transfers
    to_amount: Annotated[float, Field(gt=0)] | None = None


class TransferUpdate(BaseAPIModel):
    """Model for updating a transfer."""

    description: str | None = None
    from_amount: Annotated[float, Field(gt=0)] | None = None
    to_amount: Annotated[float, Field(gt=0)] | None = None


class TransferResponse(TransferBase):
    """Model for transfer responses."""

    id: int
    to_amount: float
    from_currency: Currency
    to_currency: Currency
    exchange_rate: float | None = None
    created_at: datetime
    updated_at: datetime


class TransferListResponse(BaseAPIModel):
    """Paginated response for transfer listings."""

    items: list[TransferResponse]
    total: int
    page: int = 1
    size: int = 10
    pages: int
