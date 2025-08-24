import csv
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from jenmoney.exceptions import ExchangeRateNotFoundError
from jenmoney.models.currency_rate import CurrencyRate
from jenmoney.schemas.currency_rate import CurrencyRateImport


class CurrencyService:
    """Service for handling currency conversions and exchange rates."""

    def __init__(self, db: Session):
        self.db = db

    def get_current_rate(
        self,
        from_currency: str,
        to_currency: str,
        date: datetime | None = None,
    ) -> Decimal:
        """Get the exchange rate for converting from one currency to another.

        Args:
            from_currency: Source currency code
            to_currency: Target currency code
            date: Date for which to get the rate (defaults to current date)

        Returns:
            Exchange rate as Decimal

        Raises:
            ExchangeRateNotFoundError: When no exchange rate is found for the currency pair
        """
        if from_currency == to_currency:
            return Decimal("1.0")

        if date is None:
            date = datetime.now(timezone.utc)

        # If converting to USD, get direct rate
        if to_currency == "USD":
            rate = self._get_rate_to_usd(from_currency, date)
            if rate is None:
                raise ExchangeRateNotFoundError(
                    from_currency=from_currency, to_currency=to_currency, date=date.isoformat()
                )
            return Decimal(str(rate))

        # If converting from USD, get inverse rate
        if from_currency == "USD":
            rate = self._get_rate_to_usd(to_currency, date)
            if rate is None:
                raise ExchangeRateNotFoundError(
                    from_currency=from_currency, to_currency=to_currency, date=date.isoformat()
                )
            return Decimal("1.0") / Decimal(str(rate))

        # For non-USD conversions, go through USD
        from_to_usd = self._get_rate_to_usd(from_currency, date)
        to_to_usd = self._get_rate_to_usd(to_currency, date)

        if from_to_usd is None:
            raise ExchangeRateNotFoundError(
                from_currency=from_currency, to_currency="USD", date=date.isoformat()
            )
        if to_to_usd is None:
            raise ExchangeRateNotFoundError(
                from_currency=to_currency, to_currency="USD", date=date.isoformat()
            )

        return Decimal(str(from_to_usd)) / Decimal(str(to_to_usd))

    def _get_rate_to_usd(self, currency: str, date: datetime) -> float | None:
        """Get the rate for converting a currency to USD."""
        if currency == "USD":
            return 1.0

        rate = (
            self.db.query(CurrencyRate)
            .filter(
                and_(
                    CurrencyRate.currency_from == currency,
                    CurrencyRate.currency_to == "USD",
                    CurrencyRate.effective_from <= date,
                    or_(
                        CurrencyRate.effective_to.is_(None),
                        CurrencyRate.effective_to >= date,
                    ),
                )
            )
            .order_by(CurrencyRate.effective_from.desc())
            .first()
        )

        return float(rate.rate) if rate else None

    def convert_amount(
        self,
        amount: Decimal,
        from_currency: str,
        to_currency: str,
        date: datetime | None = None,
    ) -> Decimal:
        """Convert an amount from one currency to another.

        Args:
            amount: Amount to convert
            from_currency: Source currency code
            to_currency: Target currency code
            date: Date for which to use exchange rate

        Returns:
            Converted amount as Decimal

        Raises:
            ExchangeRateNotFoundError: When no exchange rate is found for the currency pair
        """
        if from_currency == to_currency:
            return amount

        try:
            rate = self.get_current_rate(from_currency, to_currency, date)
            return amount * rate
        except ExchangeRateNotFoundError as e:
            # Re-raise with amount context for better debugging
            e.amount = str(amount)
            raise

    def load_rates_from_csv(self, file_path: str | Path) -> int:
        """Load exchange rates from a CSV file.

        Args:
            file_path: Path to the CSV file

        Returns:
            Number of rates loaded
        """
        file_path = Path(file_path)
        count = 0

        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                rate_import = CurrencyRateImport(
                    currency_from=row["currency_from"],  # type: ignore[arg-type]
                    rate_to_usd=float(row["rate_to_usd"]),
                    effective_from=datetime.fromisoformat(row["effective_from"]),
                    effective_to=(
                        datetime.fromisoformat(row["effective_to"])
                        if row.get("effective_to")
                        else None
                    ),
                )
                self._create_or_update_rate(rate_import)
                count += 1

        self.db.commit()
        return count

    def load_rates_from_json(self, file_path: str | Path) -> int:
        """Load exchange rates from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            Number of rates loaded
        """
        file_path = Path(file_path)
        count = 0

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            rates = data if isinstance(data, list) else data.get("rates", [])

            for rate_data in rates:
                rate_import = CurrencyRateImport(**rate_data)
                self._create_or_update_rate(rate_import)
                count += 1

        self.db.commit()
        return count

    def _create_or_update_rate(self, rate_import: CurrencyRateImport) -> None:
        """Create or update a currency rate."""
        # Check if rate already exists for this period
        existing = (
            self.db.query(CurrencyRate)
            .filter(
                and_(
                    CurrencyRate.currency_from == rate_import.currency_from,
                    CurrencyRate.currency_to == "USD",
                    CurrencyRate.effective_from == rate_import.effective_from,
                )
            )
            .first()
        )

        if existing:
            existing.rate = Decimal(str(rate_import.rate_to_usd))  # type: ignore[assignment]
            existing.effective_to = rate_import.effective_to  # type: ignore[assignment]
        else:
            new_rate = CurrencyRate(
                currency_from=rate_import.currency_from,
                currency_to="USD",
                rate=Decimal(str(rate_import.rate_to_usd)),
                effective_from=rate_import.effective_from,
                effective_to=rate_import.effective_to,
            )
            self.db.add(new_rate)

    def get_all_current_rates(self) -> dict[str, float]:
        """Get all current exchange rates to USD.

        Returns:
            Dictionary mapping currency codes to their USD exchange rates
        """
        now = datetime.now(timezone.utc)
        rates = (
            self.db.query(CurrencyRate)
            .filter(
                and_(
                    CurrencyRate.currency_to == "USD",
                    CurrencyRate.effective_from <= now,
                    or_(
                        CurrencyRate.effective_to.is_(None),
                        CurrencyRate.effective_to >= now,
                    ),
                )
            )
            .all()
        )

        result = {"USD": 1.0}
        for rate in rates:
            result[str(rate.currency_from)] = float(rate.rate)

        return result
