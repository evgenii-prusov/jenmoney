from fastapi.testclient import TestClient

from jenmoney.models.currency_rate import CurrencyRate
from jenmoney.database import get_db
from datetime import datetime, timezone
from decimal import Decimal


class TestAccountPercentage:
    def test_single_account_percentage(self, client: TestClient):
        """Test that a single account shows 100% of total"""
        # Create single account
        payload = {"name": "Only Account", "currency": "USD", "balance": 1000.00}
        response = client.post("/api/v1/accounts/", json=payload)
        account_id = response.json()["id"]

        # Get account with percentage
        response = client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["percentage_of_total"] == 1.0  # 100%

    def test_multiple_accounts_equal_percentage(self, client: TestClient):
        """Test equal distribution among accounts with same balance"""
        # Create 4 accounts with equal balance
        accounts = []
        for i in range(4):
            payload = {"name": f"Account {i + 1}", "currency": "USD", "balance": 250.00}
            response = client.post("/api/v1/accounts/", json=payload)
            accounts.append(response.json()["id"])

        # Check each account has 25%
        for account_id in accounts:
            response = client.get(f"/api/v1/accounts/{account_id}")
            assert response.status_code == 200
            data = response.json()
            assert data["percentage_of_total"] == 0.25  # 25%

    def test_accounts_list_includes_percentage(self, client: TestClient):
        """Test that account list endpoint includes percentage for each account"""
        # Create accounts with different balances
        accounts_data = [
            {"name": "Account 1", "currency": "USD", "balance": 600.00},
            {"name": "Account 2", "currency": "USD", "balance": 300.00},
            {"name": "Account 3", "currency": "USD", "balance": 100.00},
        ]

        for account_data in accounts_data:
            client.post("/api/v1/accounts/", json=account_data)

        # Get accounts list
        response = client.get("/api/v1/accounts/")
        assert response.status_code == 200
        data = response.json()

        # Sort items by balance for predictable testing
        items = sorted(data["items"], key=lambda x: x["balance"], reverse=True)

        # Check percentages (600/1000=0.6, 300/1000=0.3, 100/1000=0.1)
        assert items[0]["percentage_of_total"] == 0.6  # 60%
        assert items[1]["percentage_of_total"] == 0.3  # 30%
        assert items[2]["percentage_of_total"] == 0.1  # 10%

    def test_zero_balance_account_percentage(self, client: TestClient):
        """Test that account with zero balance shows 0%"""
        # Create accounts
        client.post(
            "/api/v1/accounts/",
            json={"name": "Rich Account", "currency": "USD", "balance": 1000.00},
        )
        response = client.post(
            "/api/v1/accounts/", json={"name": "Empty Account", "currency": "USD", "balance": 0.00}
        )
        empty_account_id = response.json()["id"]

        # Check empty account has 0%
        response = client.get(f"/api/v1/accounts/{empty_account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["percentage_of_total"] == 0.0  # 0%

    def test_percentage_with_different_currencies(self, client: TestClient):
        """Test percentage calculation with multiple currencies"""
        # First, we need to set up exchange rates
        # Get a database session to add exchange rates
        from jenmoney.main import app

        test_db = next(app.dependency_overrides[get_db]())

        # Add exchange rates (all to USD)
        rates = [
            CurrencyRate(
                currency_from="EUR",
                currency_to="USD",
                rate=Decimal("1.1"),  # 1 EUR = 1.1 USD
                effective_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
            ),
            CurrencyRate(
                currency_from="JPY",
                currency_to="USD",
                rate=Decimal("0.0067"),  # 1 JPY = 0.0067 USD
                effective_from=datetime(2024, 1, 1, tzinfo=timezone.utc),
            ),
        ]
        for rate in rates:
            test_db.add(rate)
        test_db.commit()

        # Create accounts with different currencies
        accounts_data = [
            {"name": "USD Account", "currency": "USD", "balance": 1000.00},  # $1000
            {"name": "EUR Account", "currency": "EUR", "balance": 909.09},  # ~$1000 (909.09 * 1.1)
            {
                "name": "JPY Account",
                "currency": "JPY",
                "balance": 149253.73,
            },  # ~$1000 (149253.73 * 0.0067)
        ]

        account_ids = []
        for account_data in accounts_data:
            response = client.post("/api/v1/accounts/", json=account_data)
            account_ids.append(response.json()["id"])

        # Each account should be approximately 33.33% (1/3)
        for account_id in account_ids:
            response = client.get(f"/api/v1/accounts/{account_id}")
            assert response.status_code == 200
            data = response.json()
            # Allow some tolerance for floating point calculations
            assert 0.32 <= data["percentage_of_total"] <= 0.34

        test_db.close()

    def test_percentage_updates_after_balance_change(self, client: TestClient):
        """Test that percentage is recalculated after account balance update"""
        # Create two accounts
        response1 = client.post(
            "/api/v1/accounts/", json={"name": "Account 1", "currency": "USD", "balance": 500.00}
        )
        account1_id = response1.json()["id"]

        response2 = client.post(
            "/api/v1/accounts/", json={"name": "Account 2", "currency": "USD", "balance": 500.00}
        )
        account2_id = response2.json()["id"]

        # Initially both should be 50%
        response = client.get(f"/api/v1/accounts/{account1_id}")
        assert response.json()["percentage_of_total"] == 0.5

        # Update account1 balance
        client.patch(f"/api/v1/accounts/{account1_id}", json={"balance": 1500.00})

        # Now account1 should be 75% (1500/2000)
        response = client.get(f"/api/v1/accounts/{account1_id}")
        assert response.json()["percentage_of_total"] == 0.75

        # And account2 should be 25% (500/2000)
        response = client.get(f"/api/v1/accounts/{account2_id}")
        assert response.json()["percentage_of_total"] == 0.25

    def test_percentage_after_account_deletion(self, client: TestClient):
        """Test that percentages are recalculated after account deletion"""
        # Create three accounts
        accounts = []
        for i in range(3):
            response = client.post(
                "/api/v1/accounts/",
                json={"name": f"Account {i + 1}", "currency": "USD", "balance": 100.00},
            )
            accounts.append(response.json()["id"])

        # Initially each should be ~33.33%
        response = client.get(f"/api/v1/accounts/{accounts[0]}")
        assert abs(response.json()["percentage_of_total"] - 0.33) < 0.01

        # Delete one account
        client.delete(f"/api/v1/accounts/{accounts[2]}")

        # Remaining accounts should now be 50% each
        for account_id in accounts[:2]:
            response = client.get(f"/api/v1/accounts/{account_id}")
            assert response.json()["percentage_of_total"] == 0.5

    def test_percentage_rounding(self, client: TestClient):
        """Test that percentages are properly rounded"""
        # Create accounts that will result in repeating decimals
        accounts_data = [
            {"name": "Account 1", "currency": "USD", "balance": 100.00},
            {"name": "Account 2", "currency": "USD", "balance": 200.00},
        ]

        account_ids = []
        for account_data in accounts_data:
            response = client.post("/api/v1/accounts/", json=account_data)
            account_ids.append(response.json()["id"])

        # Check first account (100/300 = 0.333... should be 0.33)
        response = client.get(f"/api/v1/accounts/{account_ids[0]}")
        assert response.json()["percentage_of_total"] == 0.33

        # Check second account (200/300 = 0.666... should be 0.67)
        response = client.get(f"/api/v1/accounts/{account_ids[1]}")
        assert response.json()["percentage_of_total"] == 0.67
