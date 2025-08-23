import json
from io import BytesIO

from fastapi.testclient import TestClient


class TestCurrencyRatesList:
    def test_list_currency_rates_empty(self, client: TestClient):
        response = client.get("/api/v1/currency-rates/")
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_list_currency_rates_with_data(self, client: TestClient):
        # Import some test rates first
        csv_content = """currency_from,rate_to_usd,effective_from
EUR,1.08,2024-01-01T00:00:00
RUB,0.011,2024-01-01T00:00:00
JPY,0.0067,2024-01-01T00:00:00"""

        file = BytesIO(csv_content.encode())
        response = client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )
        assert response.status_code == 200

        # Now list the rates
        response = client.get("/api/v1/currency-rates/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        currencies = [rate["currency_from"] for rate in data]
        assert "EUR" in currencies
        assert "RUB" in currencies
        assert "JPY" in currencies


class TestCurrencyRatesImport:
    def test_import_csv_valid(self, client: TestClient):
        csv_content = """currency_from,rate_to_usd,effective_from,effective_to
EUR,1.08,2024-01-01T00:00:00,
RUB,0.011,2024-01-01T00:00:00,
JPY,0.0067,2024-01-01T00:00:00,"""

        file = BytesIO(csv_content.encode())
        response = client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully imported 3 exchange rates"

    def test_import_csv_with_effective_dates(self, client: TestClient):
        csv_content = """currency_from,rate_to_usd,effective_from,effective_to
EUR,1.05,2023-01-01T00:00:00,2023-12-31T23:59:59
EUR,1.08,2024-01-01T00:00:00,"""

        file = BytesIO(csv_content.encode())
        response = client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully imported 2 exchange rates"

        # Verify rates were imported
        response = client.get("/api/v1/currency-rates/")
        rates = response.json()
        eur_rates = [r for r in rates if r["currency_from"] == "EUR"]
        assert len(eur_rates) == 2

    def test_import_csv_invalid_file_type(self, client: TestClient):
        file = BytesIO(b"not a csv")
        response = client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.txt", file, "text/plain")}
        )
        assert response.status_code == 400
        assert "must be a CSV" in response.json()["detail"]

    def test_import_csv_malformed_data(self, client: TestClient):
        csv_content = """currency_from,rate_to_usd,effective_from
EUR,invalid_number,2024-01-01T00:00:00"""

        file = BytesIO(csv_content.encode())
        response = client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )
        assert response.status_code == 400
        assert "Error importing rates" in response.json()["detail"]

    def test_import_json_valid(self, client: TestClient):
        json_content = {
            "rates": [
                {
                    "currency_from": "EUR",
                    "rate_to_usd": 1.08,
                    "effective_from": "2024-01-01T00:00:00",
                },
                {
                    "currency_from": "RUB",
                    "rate_to_usd": 0.011,
                    "effective_from": "2024-01-01T00:00:00",
                },
            ]
        }

        file = BytesIO(json.dumps(json_content).encode())
        response = client.post(
            "/api/v1/currency-rates/import/json",
            files={"file": ("rates.json", file, "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully imported 2 exchange rates"

    def test_import_json_list_format(self, client: TestClient):
        json_content = [
            {"currency_from": "EUR", "rate_to_usd": 1.08, "effective_from": "2024-01-01T00:00:00"},
            {
                "currency_from": "JPY",
                "rate_to_usd": 0.0067,
                "effective_from": "2024-01-01T00:00:00",
            },
        ]

        file = BytesIO(json.dumps(json_content).encode())
        response = client.post(
            "/api/v1/currency-rates/import/json",
            files={"file": ("rates.json", file, "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Successfully imported 2 exchange rates"

    def test_import_json_invalid_file_type(self, client: TestClient):
        file = BytesIO(b"not json")
        response = client.post(
            "/api/v1/currency-rates/import/json", files={"file": ("rates.txt", file, "text/plain")}
        )
        assert response.status_code == 400
        assert "must be JSON" in response.json()["detail"]

    def test_import_json_malformed_data(self, client: TestClient):
        file = BytesIO(b"{invalid json}")
        response = client.post(
            "/api/v1/currency-rates/import/json",
            files={"file": ("rates.json", file, "application/json")},
        )
        assert response.status_code == 400
        assert "Error importing rates" in response.json()["detail"]


class TestCurrentRates:
    def test_get_current_rates_empty(self, client: TestClient):
        response = client.get("/api/v1/currency-rates/current")
        assert response.status_code == 200
        data = response.json()
        assert data == {"USD": 1.0}

    def test_get_current_rates_with_data(self, client: TestClient):
        # Import rates
        csv_content = """currency_from,rate_to_usd,effective_from
EUR,1.08,2024-01-01T00:00:00
RUB,0.011,2024-01-01T00:00:00
JPY,0.0067,2024-01-01T00:00:00"""

        file = BytesIO(csv_content.encode())
        client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )

        # Get current rates
        response = client.get("/api/v1/currency-rates/current")
        assert response.status_code == 200
        data = response.json()
        assert data["USD"] == 1.0
        assert data["EUR"] == 1.08
        assert data["RUB"] == 0.011
        assert data["JPY"] == 0.0067

    def test_get_current_rates_with_expired(self, client: TestClient):
        # Import rates with one expired
        csv_content = """currency_from,rate_to_usd,effective_from,effective_to
EUR,1.05,2023-01-01T00:00:00,2023-12-31T23:59:59
EUR,1.08,2024-01-01T00:00:00,
RUB,0.011,2024-01-01T00:00:00,"""

        file = BytesIO(csv_content.encode())
        client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )

        # Get current rates (should only show non-expired)
        response = client.get("/api/v1/currency-rates/current")
        assert response.status_code == 200
        data = response.json()
        assert data["EUR"] == 1.08  # Should get the current rate, not the expired one
        assert data["RUB"] == 0.011

    def test_update_existing_rate(self, client: TestClient):
        # Import initial rate
        csv_content1 = """currency_from,rate_to_usd,effective_from
EUR,1.05,2024-01-01T00:00:00"""

        file = BytesIO(csv_content1.encode())
        client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )

        # Import updated rate for same period
        csv_content2 = """currency_from,rate_to_usd,effective_from
EUR,1.08,2024-01-01T00:00:00"""

        file = BytesIO(csv_content2.encode())
        response = client.post(
            "/api/v1/currency-rates/import/csv", files={"file": ("rates.csv", file, "text/csv")}
        )
        assert response.status_code == 200

        # Verify rate was updated, not duplicated
        response = client.get("/api/v1/currency-rates/current")
        data = response.json()
        assert data["EUR"] == 1.08

        # Check there's still only one EUR rate
        response = client.get("/api/v1/currency-rates/")
        rates = response.json()
        eur_rates = [
            r
            for r in rates
            if r["currency_from"] == "EUR" and r["effective_from"].startswith("2024-01-01")
        ]
        assert len(eur_rates) == 1
