from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from jenmoney.services.currency_service import CurrencyService


@pytest.fixture
def currency_service(db, client: TestClient):
    """Fixture that provides a CurrencyService with test data."""
    # Import test rates
    csv_content = """currency_from,rate_to_usd,effective_from
EUR,1.08,2024-01-01T00:00:00
RUB,0.011,2024-01-01T00:00:00
JPY,0.0067,2024-01-01T00:00:00"""

    file = BytesIO(csv_content.encode())
    response = client.post(
        "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
    )
    assert response.status_code == 200

    # Get a database session from the client
    from jenmoney.database import get_db
    from jenmoney.main import app

    db_session = next(app.dependency_overrides[get_db]())
    return CurrencyService(db_session)


class TestCurrencyConversion:
    def test_same_currency_conversion(self, currency_service: CurrencyService):
        rate = currency_service.get_current_rate("USD", "USD")
        assert rate == Decimal("1.0")

        amount = currency_service.convert_amount(Decimal("100"), "USD", "USD")
        assert amount == Decimal("100")

    def test_currency_to_usd(self, currency_service: CurrencyService):
        # EUR to USD
        rate = currency_service.get_current_rate("EUR", "USD")
        assert rate == Decimal("1.08")

        amount = currency_service.convert_amount(Decimal("100"), "EUR", "USD")
        assert amount == Decimal("108")

        # RUB to USD
        rate = currency_service.get_current_rate("RUB", "USD")
        assert rate == Decimal("0.011")

        amount = currency_service.convert_amount(Decimal("1000"), "RUB", "USD")
        assert amount == Decimal("11")

    def test_usd_to_currency(self, currency_service: CurrencyService):
        # USD to EUR
        rate = currency_service.get_current_rate("USD", "EUR")
        assert abs(rate - Decimal("0.925926")) < Decimal("0.000001")  # 1/1.08

        amount = currency_service.convert_amount(Decimal("108"), "USD", "EUR")
        assert abs(amount - Decimal("100")) < Decimal("0.01")

        # USD to JPY
        rate = currency_service.get_current_rate("USD", "JPY")
        expected_rate = Decimal("1") / Decimal("0.0067")
        assert abs(rate - expected_rate) < Decimal("0.01")

    def test_cross_currency_conversion(self, currency_service: CurrencyService):
        # EUR to RUB (through USD)
        rate = currency_service.get_current_rate("EUR", "RUB")
        # EUR->USD: 1.08, USD->RUB: 1/0.011 = 90.909
        # EUR->RUB: 1.08 * 90.909 = 98.18
        expected_rate = Decimal("1.08") / Decimal("0.011")
        assert abs(rate - expected_rate) < Decimal("0.01")

        amount = currency_service.convert_amount(Decimal("100"), "EUR", "RUB")
        expected_amount = Decimal("100") * expected_rate
        assert abs(amount - expected_amount) < Decimal("1")

        # JPY to EUR (through USD)
        rate = currency_service.get_current_rate("JPY", "EUR")
        # JPY->USD: 0.0067, USD->EUR: 1/1.08
        # JPY->EUR: 0.0067 / 1.08
        expected_rate = Decimal("0.0067") / Decimal("1.08")
        assert abs(rate - expected_rate) < Decimal("0.0001")

    def test_missing_exchange_rate(self, db, client: TestClient):
        # Create service without any rates
        from jenmoney.database import get_db
        from jenmoney.main import app

        db_session = next(app.dependency_overrides[get_db]())
        service = CurrencyService(db_session)

        # Should return 1.0 when rate is missing
        rate = service.get_current_rate("GBP", "USD")
        assert rate == Decimal("1.0")

        amount = service.convert_amount(Decimal("100"), "GBP", "USD")
        assert amount == Decimal("100")

    def test_conversion_with_date(self, db, client: TestClient):
        # Import rates with different effective dates
        csv_content = """currency_from,rate_to_usd,effective_from,effective_to
EUR,1.05,2023-01-01T00:00:00,2023-12-31T23:59:59
EUR,1.08,2024-01-01T00:00:00,"""

        file = BytesIO(csv_content.encode())
        response = client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )
        assert response.status_code == 200

        from jenmoney.database import get_db
        from jenmoney.main import app

        db_session = next(app.dependency_overrides[get_db]())
        service = CurrencyService(db_session)

        # Get rate for 2023 date
        old_date = datetime(2023, 6, 1, tzinfo=timezone.utc)
        rate = service.get_current_rate("EUR", "USD", old_date)
        assert rate == Decimal("1.05")

        # Get rate for 2024 date
        new_date = datetime(2024, 6, 1, tzinfo=timezone.utc)
        rate = service.get_current_rate("EUR", "USD", new_date)
        assert rate == Decimal("1.08")

        # Get current rate (should be 2024 rate)
        rate = service.get_current_rate("EUR", "USD")
        assert rate == Decimal("1.08")

    def test_precision_handling(self, currency_service: CurrencyService):
        # Test with high precision amounts
        amount = currency_service.convert_amount(Decimal("123.456789"), "EUR", "USD")
        expected = Decimal("123.456789") * Decimal("1.08")
        assert abs(amount - expected) < Decimal("0.000001")

        # Test with very small amounts
        amount = currency_service.convert_amount(Decimal("0.001"), "RUB", "USD")
        expected = Decimal("0.001") * Decimal("0.011")
        assert abs(amount - expected) < Decimal("0.000001")

    def test_get_all_current_rates(self, currency_service: CurrencyService):
        rates = currency_service.get_all_current_rates()

        assert rates["USD"] == 1.0
        assert rates["EUR"] == 1.08
        assert rates["RUB"] == 0.011
        assert rates["JPY"] == 0.0067
        assert len(rates) == 4

    def test_rate_priority_latest_effective(self, db, client: TestClient):
        # Import multiple rates for same currency with different effective dates
        csv_content = """currency_from,rate_to_usd,effective_from
EUR,1.05,2024-01-01T00:00:00
EUR,1.06,2024-02-01T00:00:00
EUR,1.08,2024-03-01T00:00:00"""

        file = BytesIO(csv_content.encode())
        response = client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )
        assert response.status_code == 200

        from jenmoney.database import get_db
        from jenmoney.main import app

        db_session = next(app.dependency_overrides[get_db]())
        service = CurrencyService(db_session)

        # Should get the latest rate
        current_date = datetime(2024, 4, 1, tzinfo=timezone.utc)
        rate = service.get_current_rate("EUR", "USD", current_date)
        assert rate == Decimal("1.08")

        # Check for date in between rates
        mid_date = datetime(2024, 2, 15, tzinfo=timezone.utc)
        rate = service.get_current_rate("EUR", "USD", mid_date)
        assert rate == Decimal("1.06")
