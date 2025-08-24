"""
Initialize default exchange rates for common currencies.
This provides basic rates so the app works out of the box with currency conversion.
"""
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from jenmoney.models.currency_rate import CurrencyRate


def initialize_default_exchange_rates(db: Session) -> None:
    """Initialize basic exchange rates for common currencies to USD.
    
    This provides default rates so the app works out of the box.
    Users can update these rates later through the API.
    """
    # Check if any rates already exist
    existing_rates = db.query(CurrencyRate).first()
    if existing_rates:
        # Don't overwrite existing rates
        return
    
    # Basic exchange rates to USD (approximate values as of 2024)
    # These are reasonable defaults that users can update
    default_rates = [
        ("EUR", "1.08"),  # 1 EUR = 1.08 USD
        ("GBP", "1.26"),  # 1 GBP = 1.26 USD  
        ("JPY", "0.0067"),  # 1 JPY = 0.0067 USD
        ("CAD", "0.74"),  # 1 CAD = 0.74 USD
        ("AUD", "0.66"),  # 1 AUD = 0.66 USD
        ("CHF", "1.10"),  # 1 CHF = 1.10 USD
        ("CNY", "0.14"),  # 1 CNY = 0.14 USD
        ("RUB", "0.011"), # 1 RUB = 0.011 USD
    ]
    
    effective_from = datetime.now(timezone.utc)
    
    for currency_from, rate_str in default_rates:
        rate = CurrencyRate(
            currency_from=currency_from,
            currency_to="USD",
            rate=Decimal(rate_str),
            effective_from=effective_from,
            effective_to=None,  # No end date - these are ongoing rates
        )
        db.add(rate)
    
    db.commit()