from decimal import Decimal
from typing import Any, cast

from sqlalchemy.orm import Session

from jenmoney.crud.user_settings import user_settings
from jenmoney.exceptions import CurrencyConversionError, ExchangeRateNotFoundError
from jenmoney.models.account import Account
from jenmoney.services.currency_service import CurrencyService


class AccountEnrichmentService:
    """Service for enriching account data with currency conversions and analytics."""

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
            except ExchangeRateNotFoundError as e:
                raise CurrencyConversionError(
                    message=f"Failed to convert account '{account.name}' balance from {account.currency} to {settings.default_currency}",
                    from_currency=str(account.currency),
                    to_currency=str(settings.default_currency),
                    amount=str(account.balance),
                    original_error=e,
                ) from e

        return account_dict

    def get_account_percentage(self, account_id: int) -> float:
        """Calculate the percentage of total portfolio value for a specific account.

        Args:
            account_id: The ID of the account to calculate percentage for

        Returns:
            The percentage of total portfolio value (0.0 to 1.0)
            
        Raises:
            CurrencyConversionError: When currency conversion fails for any account
        """
        accounts: list[Account] = self.db.query(Account).all()
        if not accounts:
            return 0.0

        total_usd: Decimal = Decimal("0")
        target_usd: Decimal | None = None

        for acc in accounts:
            try:
                # Cast because SQLAlchemy attribute is typed as Column[Decimal] for Pylance
                usd_amount = Decimal(
                    str(
                        self.currency_service.convert_amount(
                            amount=cast(Decimal, acc.balance),
                            from_currency=cast(str, acc.currency),
                            to_currency="USD",
                        )
                    )
                )
                total_usd += usd_amount
                if cast(int, acc.id) == account_id:
                    target_usd = usd_amount
            except ExchangeRateNotFoundError as e:
                raise CurrencyConversionError(
                    message=f"Failed to convert account '{acc.name}' balance to USD for percentage calculation",
                    from_currency=str(acc.currency),
                    to_currency="USD", 
                    amount=str(acc.balance),
                    original_error=e,
                ) from e

        if total_usd == 0 or target_usd is None:
            return 0.0

        return float(round(target_usd / total_usd, 2))

    def enrich_account_full(self, account: Account) -> dict[str, Any]:
        """Enrich account data with both currency conversion and percentage information.

        Args:
            account: The account model instance to enrich

        Returns:
            Dictionary containing enriched account data with percentage of total
        """
        enriched_account = self.enrich_account_with_conversion(account)
        enriched_account["percentage_of_total"] = self.get_account_percentage(cast(int, account.id))
        return enriched_account
