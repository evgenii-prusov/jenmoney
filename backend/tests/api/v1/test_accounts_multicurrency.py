from io import BytesIO

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def setup_exchange_rates(client: TestClient):
    """Setup exchange rates for all tests in this module."""
    csv_content = """currency_from,rate_to_usd,effective_from
EUR,1.08,2024-01-01T00:00:00
RUB,0.011,2024-01-01T00:00:00
JPY,0.0067,2024-01-01T00:00:00"""

    file = BytesIO(csv_content.encode())
    response = client.post(
        "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
    )
    assert response.status_code == 200


class TestAccountCurrencyConversion:
    def test_create_account_with_currency_conversion_info(self, client: TestClient):
        # Create account in EUR
        response = client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 1000}
        )
        assert response.status_code == 200
        data = response.json()

        # Check basic fields
        assert data["currency"] == "EUR"
        assert data["balance"] == 1000.0

        # Check conversion fields (default currency is USD)
        assert data["default_currency"] == "USD"
        assert data["balance_in_default_currency"] == 1080.0  # 1000 * 1.08
        assert data["exchange_rate_used"] == 1.08

    def test_create_account_same_currency_no_conversion(self, client: TestClient):
        # Create account in USD (same as default)
        response = client.post(
            "/api/v1/accounts/", json={"name": "USD Account", "currency": "USD", "balance": 1000}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["currency"] == "USD"
        assert data["balance"] == 1000.0
        assert data["default_currency"] == "USD"
        # No conversion needed
        assert data["balance_in_default_currency"] is None
        assert data["exchange_rate_used"] is None

    def test_get_account_with_conversion(self, client: TestClient):
        # Create account in JPY
        create_response = client.post(
            "/api/v1/accounts/", json={"name": "JPY Account", "currency": "JPY", "balance": 10000}
        )
        account_id = create_response.json()["id"]

        # Get account details
        response = client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        data = response.json()

        assert data["currency"] == "JPY"
        assert data["balance"] == 10000.0
        assert data["default_currency"] == "USD"
        assert data["balance_in_default_currency"] == 67.0  # 10000 * 0.0067
        assert data["exchange_rate_used"] == 0.0067

    def test_list_accounts_with_conversion(self, client: TestClient):
        # Create multiple accounts in different currencies
        accounts_data = [
            {"name": "USD Account", "currency": "USD", "balance": 1000},
            {"name": "EUR Account", "currency": "EUR", "balance": 500},
            {"name": "RUB Account", "currency": "RUB", "balance": 50000},
            {"name": "JPY Account", "currency": "JPY", "balance": 100000},
        ]

        for account in accounts_data:
            client.post("/api/v1/accounts/", json=account)

        # List all accounts
        response = client.get("/api/v1/accounts/")
        assert response.status_code == 200
        data = response.json()

        assert data["total"] == 4
        items = data["items"]

        # Check each account has proper conversion info
        for item in items:
            assert "default_currency" in item
            assert item["default_currency"] == "USD"

            if item["currency"] == "USD":
                assert item["balance_in_default_currency"] is None
                assert item["exchange_rate_used"] is None
            elif item["currency"] == "EUR":
                assert item["balance_in_default_currency"] == 540.0  # 500 * 1.08
                assert item["exchange_rate_used"] == 1.08
            elif item["currency"] == "RUB":
                assert item["balance_in_default_currency"] == 550.0  # 50000 * 0.011
                assert item["exchange_rate_used"] == 0.011
            elif item["currency"] == "JPY":
                assert item["balance_in_default_currency"] == 670.0  # 100000 * 0.0067
                assert item["exchange_rate_used"] == 0.0067

    def test_update_account_preserves_conversion(self, client: TestClient):
        # Create account in EUR
        create_response = client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 1000}
        )
        account_id = create_response.json()["id"]

        # Update balance
        response = client.patch(f"/api/v1/accounts/{account_id}", json={"balance": 2000})
        assert response.status_code == 200
        data = response.json()

        assert data["balance"] == 2000.0
        assert data["balance_in_default_currency"] == 2160.0  # 2000 * 1.08
        assert data["exchange_rate_used"] == 1.08

        # Update currency
        response = client.patch(f"/api/v1/accounts/{account_id}", json={"currency": "RUB"})
        assert response.status_code == 200
        data = response.json()

        assert data["currency"] == "RUB"
        assert data["balance"] == 2000.0  # Balance unchanged
        assert data["balance_in_default_currency"] == 22.0  # 2000 * 0.011
        assert data["exchange_rate_used"] == 0.011

    def test_delete_account_returns_conversion(self, client: TestClient):
        # Create account in EUR
        create_response = client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 750}
        )
        account_id = create_response.json()["id"]

        # Delete account
        response = client.delete(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        data = response.json()

        # Deleted account response should include conversion info
        assert data["currency"] == "EUR"
        assert data["balance"] == 750.0
        assert data["balance_in_default_currency"] == 810.0  # 750 * 1.08
        assert data["exchange_rate_used"] == 1.08


class TestAccountWithDifferentDefaultCurrency:
    def test_account_conversion_with_eur_default(self, client: TestClient):
        # Change default currency to EUR
        client.patch("/api/v1/settings/", json={"default_currency": "EUR"})

        # Create account in USD
        response = client.post(
            "/api/v1/accounts/", json={"name": "USD Account", "currency": "USD", "balance": 1080}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["default_currency"] == "EUR"
        assert abs(data["balance_in_default_currency"] - 1000.0) < 0.01  # 1080 / 1.08
        assert abs(data["exchange_rate_used"] - 0.925926) < 0.000001  # 1/1.08

    def test_account_conversion_with_rub_default(self, client: TestClient):
        # Change default currency to RUB
        client.patch("/api/v1/settings/", json={"default_currency": "RUB"})

        # Create account in EUR
        response = client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 100}
        )
        assert response.status_code == 200
        data = response.json()

        assert data["default_currency"] == "RUB"
        # EUR to RUB: 100 * (1.08 / 0.011) ≈ 9818.18
        assert abs(data["balance_in_default_currency"] - 9818.18) < 1
        assert abs(data["exchange_rate_used"] - 98.1818) < 0.01

    def test_account_conversion_with_jpy_default(self, client: TestClient):
        # Change default currency to JPY
        client.patch("/api/v1/settings/", json={"default_currency": "JPY"})

        # Create accounts in different currencies
        usd_response = client.post(
            "/api/v1/accounts/", json={"name": "USD Account", "currency": "USD", "balance": 100}
        )
        usd_data = usd_response.json()

        # USD to JPY: 100 / 0.0067 ≈ 14925.37
        assert abs(usd_data["balance_in_default_currency"] - 14925.37) < 1

        eur_response = client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 100}
        )
        eur_data = eur_response.json()

        # EUR to JPY: 100 * (1.08 / 0.0067) ≈ 16119.40
        assert abs(eur_data["balance_in_default_currency"] - 16119.40) < 1


class TestAccountsWithMissingRates:
    def test_account_with_missing_exchange_rate(self, client: TestClient):
        # Clear all rates first
        from jenmoney.database import get_db
        from jenmoney.main import app
        from jenmoney.models.currency_rate import CurrencyRate

        db_session = next(app.dependency_overrides[get_db]())
        db_session.query(CurrencyRate).delete()
        db_session.commit()

        # Create account in EUR (no rates available)
        response = client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 1000}
        )
        assert response.status_code == 200
        data = response.json()

        # Should handle missing rate by using 1.0 as default
        assert data["currency"] == "EUR"
        assert data["balance"] == 1000.0
        assert data["default_currency"] == "USD"
        # Uses 1.0 as default rate when missing
        assert data["balance_in_default_currency"] == 1000.0
        assert data["exchange_rate_used"] == 1.0

    def test_list_accounts_mixed_rates(self, client: TestClient):
        # Import only EUR rate
        from jenmoney.database import get_db
        from jenmoney.main import app
        from jenmoney.models.currency_rate import CurrencyRate

        db_session = next(app.dependency_overrides[get_db]())
        db_session.query(CurrencyRate).delete()
        db_session.commit()

        csv_content = """currency_from,rate_to_usd,effective_from
EUR,1.08,2024-01-01T00:00:00"""

        file = BytesIO(csv_content.encode())
        client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )

        # Create accounts in EUR (has rate) and RUB (no rate)
        client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 1000}
        )
        client.post(
            "/api/v1/accounts/", json={"name": "RUB Account", "currency": "RUB", "balance": 50000}
        )

        # List accounts
        response = client.get("/api/v1/accounts/")
        assert response.status_code == 200
        items = response.json()["items"]

        # EUR account should have conversion
        eur_account = next(acc for acc in items if acc["currency"] == "EUR")
        assert eur_account["balance_in_default_currency"] == 1080.0

        # RUB account uses 1.0 as default rate when missing
        rub_account = next(acc for acc in items if acc["currency"] == "RUB")
        assert rub_account["balance_in_default_currency"] == 50000.0  # Uses 1.0 rate


class TestTotalBalance:
    def test_total_balance_single_currency(self, client: TestClient):
        # Create accounts all in USD
        for i in range(3):
            client.post(
                "/api/v1/accounts/",
                json={"name": f"USD Account {i}", "currency": "USD", "balance": 1000},
            )

        response = client.get("/api/v1/accounts/total-balance/")
        assert response.status_code == 200
        data = response.json()

        assert data["total_balance"] == 3000.0
        assert data["default_currency"] == "USD"
        assert data["currency_breakdown"] == {"USD": 3000.0}

    def test_total_balance_mixed_currencies(self, client: TestClient):
        # Create accounts in different currencies
        accounts = [
            {"name": "USD Account", "currency": "USD", "balance": 1000},
            {"name": "EUR Account", "currency": "EUR", "balance": 500},
            {"name": "RUB Account", "currency": "RUB", "balance": 10000},
            {"name": "JPY Account", "currency": "JPY", "balance": 100000},
        ]

        for account in accounts:
            client.post("/api/v1/accounts/", json=account)

        response = client.get("/api/v1/accounts/total-balance/")
        assert response.status_code == 200
        data = response.json()

        # Total in USD: 1000 + 500*1.08 + 10000*0.011 + 100000*0.0067
        # = 1000 + 540 + 110 + 670 = 2320
        assert data["total_balance"] == 2320.0
        assert data["default_currency"] == "USD"
        assert data["currency_breakdown"] == {
            "USD": 1000.0,
            "EUR": 500.0,
            "RUB": 10000.0,
            "JPY": 100000.0,
        }

    def test_total_balance_with_different_default_currency(self, client: TestClient):
        # Create accounts
        accounts = [
            {"name": "USD Account", "currency": "USD", "balance": 1080},
            {"name": "EUR Account", "currency": "EUR", "balance": 1000},
        ]

        for account in accounts:
            client.post("/api/v1/accounts/", json=account)

        # Change default to EUR
        client.patch("/api/v1/settings/", json={"default_currency": "EUR"})

        response = client.get("/api/v1/accounts/total-balance/")
        assert response.status_code == 200
        data = response.json()

        # Total in EUR: 1080/1.08 + 1000 = 1000 + 1000 = 2000
        assert abs(data["total_balance"] - 2000.0) < 0.01
        assert data["default_currency"] == "EUR"
        assert data["currency_breakdown"] == {"USD": 1080.0, "EUR": 1000.0}

    def test_total_balance_empty_accounts(self, client: TestClient):
        response = client.get("/api/v1/accounts/total-balance/")
        assert response.status_code == 200
        data = response.json()

        assert data["total_balance"] == 0.0
        assert data["default_currency"] == "USD"
        assert data["currency_breakdown"] == {}

    def test_total_balance_with_zero_balances(self, client: TestClient):
        # Create accounts with zero balances
        accounts = [
            {"name": "USD Account", "currency": "USD", "balance": 0},
            {"name": "EUR Account", "currency": "EUR", "balance": 0},
        ]

        for account in accounts:
            client.post("/api/v1/accounts/", json=account)

        response = client.get("/api/v1/accounts/total-balance/")
        assert response.status_code == 200
        data = response.json()

        assert data["total_balance"] == 0.0
        assert data["currency_breakdown"] == {"USD": 0.0, "EUR": 0.0}

    def test_total_balance_with_missing_rates(self, client: TestClient):
        # Clear RUB rate
        from jenmoney.database import get_db
        from jenmoney.main import app
        from jenmoney.models.currency_rate import CurrencyRate

        db_session = next(app.dependency_overrides[get_db]())
        db_session.query(CurrencyRate).filter(CurrencyRate.currency_from == "RUB").delete()
        db_session.commit()

        # Create accounts
        accounts = [
            {"name": "USD Account", "currency": "USD", "balance": 1000},
            {"name": "EUR Account", "currency": "EUR", "balance": 500},
            {"name": "RUB Account", "currency": "RUB", "balance": 50000},  # No rate
        ]

        for account in accounts:
            client.post("/api/v1/accounts/", json=account)

        response = client.get("/api/v1/accounts/total-balance/")
        assert response.status_code == 200
        data = response.json()

        # RUB uses 1.0 as default rate when missing
        assert data["total_balance"] == 51540.0  # 1000 + 500*1.08 + 50000*1.0
        assert data["currency_breakdown"] == {
            "USD": 1000.0,
            "EUR": 500.0,
            "RUB": 50000.0,  # Still shown in breakdown
        }
