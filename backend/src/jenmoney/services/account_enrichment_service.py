from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from jenmoney.crud.user_settings import user_settings
from jenmoney.models.account import Account
from jenmoney.services.currency_service import CurrencyService


class AccountEnrichmentService:
    """Service for enriching account data with additional information like currency conversions."""

    def __init__(self, db: Session):
        self.db = db
        self.currency_service = CurrencyService(db)

    def enrich_account_with_conversion(self, account: Account) -> dict[str, Any]:
        """Enrich account data with currency conversion information.
        
        Args:
            account: The account model instance to enrich
            
        Returns:
            Dictionary containing account data with currency conversion information
        """
        settings = user_settings.get_or_create(self.db)
        account_dict = {
            "id": account.id,
            "name": account.name,
            "currency": account.currency,
            "balance": float(account.balance),
            "description": account.description,
            "created_at": account.created_at,
            "updated_at": account.updated_at,
            "default_currency": settings.default_currency,
            "balance_in_default_currency": None,
            "exchange_rate_used": None,
        }

        if account.currency != settings.default_currency:
            try:
                rate = self.currency_service.get_current_rate(
                    str(account.currency), str(settings.default_currency)
                )
                converted_balance = self.currency_service.convert_amount(
                    Decimal(str(account.balance)),
                    str(account.currency),
                    str(settings.default_currency),
                )
                account_dict["balance_in_default_currency"] = float(converted_balance)
                account_dict["exchange_rate_used"] = float(rate)
            except Exception:
                # If conversion fails, leave as None
                pass

        return account_dict