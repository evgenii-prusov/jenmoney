from datetime import datetime

from jenmoney.schemas.account import Currency
from jenmoney.schemas.base import BaseAPIModel


class UserSettingsBase(BaseAPIModel):
    """Base user settings model."""

    default_currency: Currency = Currency.USD


class UserSettingsCreate(UserSettingsBase):
    """Model for creating user settings."""

    pass


class UserSettingsUpdate(BaseAPIModel):
    """Model for updating user settings."""

    default_currency: Currency | None = None


class UserSettingsResponse(UserSettingsBase):
    """Model for user settings responses."""

    id: int
    created_at: datetime
    updated_at: datetime
