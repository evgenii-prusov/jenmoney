from fastapi.testclient import TestClient


class TestUserSettings:
    def test_get_default_settings(self, client: TestClient):
        response = client.get("/api/v1/settings/")
        assert response.status_code == 200
        data = response.json()
        assert data["default_currency"] == "USD"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_settings_creates_if_not_exists(self, client: TestClient):
        # First call creates settings
        response1 = client.get("/api/v1/settings/")
        assert response1.status_code == 200
        data1 = response1.json()
        settings_id = data1["id"]

        # Second call returns same settings
        response2 = client.get("/api/v1/settings/")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["id"] == settings_id

    def test_update_settings_currency(self, client: TestClient):
        # Get initial settings
        response = client.get("/api/v1/settings/")
        assert response.status_code == 200
        initial_data = response.json()
        assert initial_data["default_currency"] == "USD"

        # Update to EUR
        response = client.patch("/api/v1/settings/", json={"default_currency": "EUR"})
        assert response.status_code == 200
        data = response.json()
        assert data["default_currency"] == "EUR"
        assert data["id"] == initial_data["id"]

        # Verify update persisted
        response = client.get("/api/v1/settings/")
        assert response.status_code == 200
        assert response.json()["default_currency"] == "EUR"

    def test_update_settings_all_supported_currencies(self, client: TestClient):
        currencies = ["EUR", "USD", "RUB", "JPY"]

        for currency in currencies:
            response = client.patch("/api/v1/settings/", json={"default_currency": currency})
            assert response.status_code == 200
            assert response.json()["default_currency"] == currency

    def test_update_settings_invalid_currency(self, client: TestClient):
        response = client.patch("/api/v1/settings/", json={"default_currency": "GBP"})
        assert response.status_code == 422

        response = client.patch("/api/v1/settings/", json={"default_currency": "INVALID"})
        assert response.status_code == 422

    def test_update_settings_empty_request(self, client: TestClient):
        # Get current settings
        initial_response = client.get("/api/v1/settings/")
        initial_currency = initial_response.json()["default_currency"]

        # Empty update should not change anything
        response = client.patch("/api/v1/settings/", json={})
        assert response.status_code == 200
        assert response.json()["default_currency"] == initial_currency

    def test_update_settings_partial(self, client: TestClient):
        # Set to EUR first
        client.patch("/api/v1/settings/", json={"default_currency": "EUR"})

        # Update with additional fields (should ignore unknown fields)
        response = client.patch(
            "/api/v1/settings/",
            json={"default_currency": "JPY", "unknown_field": "should_be_ignored"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["default_currency"] == "JPY"
        assert "unknown_field" not in data

    def test_settings_timestamps(self, client: TestClient):
        # Get initial settings
        response = client.get("/api/v1/settings/")
        assert response.status_code == 200
        initial_data = response.json()
        created_at = initial_data["created_at"]
        updated_at = initial_data["updated_at"]

        # Update settings
        response = client.patch("/api/v1/settings/", json={"default_currency": "RUB"})
        assert response.status_code == 200
        updated_data = response.json()

        # Created_at should remain the same
        assert updated_data["created_at"] == created_at
        # Updated_at should be different
        assert updated_data["updated_at"] != updated_at

    def test_settings_persistence_across_requests(self, client: TestClient):
        # Set currency to EUR
        response = client.patch("/api/v1/settings/", json={"default_currency": "EUR"})
        assert response.status_code == 200
        settings_id = response.json()["id"]

        # Create some accounts (this shouldn't affect settings)
        client.post("/api/v1/accounts/", json={"name": "Test Account"})

        # Settings should still be EUR
        response = client.get("/api/v1/settings/")
        assert response.status_code == 200
        data = response.json()
        assert data["default_currency"] == "EUR"
        assert data["id"] == settings_id


class TestSettingsIntegration:
    def test_settings_affect_account_response(self, client: TestClient):
        from io import BytesIO

        # Import exchange rates
        csv_content = """currency_from,rate_to_usd,effective_from
EUR,1.08,2024-01-01T00:00:00
RUB,0.011,2024-01-01T00:00:00"""

        file = BytesIO(csv_content.encode())
        client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )

        # Create account in EUR
        response = client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 100}
        )
        assert response.status_code == 200
        account_id = response.json()["id"]

        # With default USD settings
        response = client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["default_currency"] == "USD"
        assert data["balance_in_default_currency"] == 108.0  # 100 EUR * 1.08
        assert data["exchange_rate_used"] == 1.08

        # Change default currency to RUB
        client.patch("/api/v1/settings/", json={"default_currency": "RUB"})

        # Check account response with new default currency
        response = client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["default_currency"] == "RUB"
        # EUR to RUB: 100 * (1.08 / 0.011) ≈ 9818.18
        assert abs(data["balance_in_default_currency"] - 9818.18) < 1
        assert abs(data["exchange_rate_used"] - 98.1818) < 0.01

    def test_settings_affect_total_balance(self, client: TestClient):
        from io import BytesIO

        # Import exchange rates
        csv_content = """currency_from,rate_to_usd,effective_from
EUR,1.08,2024-01-01T00:00:00"""

        file = BytesIO(csv_content.encode())
        client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )

        # Create accounts in different currencies
        client.post(
            "/api/v1/accounts/", json={"name": "USD Account", "currency": "USD", "balance": 1000}
        )
        client.post(
            "/api/v1/accounts/", json={"name": "EUR Account", "currency": "EUR", "balance": 500}
        )

        # Get total with USD default
        response = client.get("/api/v1/accounts/total-balance/")
        assert response.status_code == 200
        data = response.json()
        assert data["default_currency"] == "USD"
        assert data["total_balance"] == 1540.0  # 1000 USD + 500 EUR * 1.08

        # Change default to EUR
        client.patch("/api/v1/settings/", json={"default_currency": "EUR"})

        # Get total with EUR default
        response = client.get("/api/v1/accounts/total-balance/")
        assert response.status_code == 200
        data = response.json()
        assert data["default_currency"] == "EUR"
        # 1000 USD / 1.08 + 500 EUR ≈ 925.93 + 500 = 1425.93
        assert abs(data["total_balance"] - 1425.93) < 1
