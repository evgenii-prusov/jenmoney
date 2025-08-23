from decimal import Decimal
from typing import cast
from sqlalchemy.orm import Session

from jenmoney.models.account import Account
from jenmoney.services.currency_service import CurrencyService


class AccountAnalyticService:
    """Service for handling analytics for accounts"""

    def get_account_percentage(self, db: Session, account_id: int) -> float:
        currency_service: CurrencyService = CurrencyService(db)
        accounts: list[Account] = db.query(Account).all()
        if not accounts:
            return 0.0

        total_usd: Decimal = Decimal("0")
        target_usd: Decimal | None = None

        for acc in accounts:
            # Cast because SQLAlchemy attribute is typed as Column[Decimal] for Pylance
            usd_amount = Decimal(
                str(
                    currency_service.convert_amount(
                        amount=cast(Decimal, acc.balance),
                        from_currency=cast(str, acc.currency),
                        to_currency="USD",
                    )
                )
            )
            total_usd += usd_amount
            if cast(int, acc.id) == account_id:
                target_usd = usd_amount

        if total_usd == 0 or target_usd is None:
            return 0.0

        return float(round(target_usd / total_usd, 2))
