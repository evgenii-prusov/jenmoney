from fastapi.testclient import TestClient


class TestAccountCreate:
    def test_create_account_with_all_fields(self, client: TestClient):
        payload = {
            "name": "Test Account",
            "currency": "USD",
            "balance": 1000.50,
            "description": "Test description",
        }
        response = client.post("/api/v1/accounts/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["currency"] == payload["currency"]
        assert data["balance"] == payload["balance"]
        assert data["description"] == payload["description"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_account_minimal_fields(self, client: TestClient):
        payload = {"name": "Minimal Account"}
        response = client.post("/api/v1/accounts/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == payload["name"]
        assert data["currency"] == "EUR"
        assert data["balance"] == 0.0
        assert data["description"] is None

    def test_create_account_with_different_currencies(self, client: TestClient):
        currencies = ["EUR", "USD", "RUB", "JPY"]
        for currency in currencies:
            payload = {"name": f"Account {currency}", "currency": currency}
            response = client.post("/api/v1/accounts/", json=payload)
            assert response.status_code == 200
            assert response.json()["currency"] == currency

    def test_create_account_invalid_currency(self, client: TestClient):
        payload = {"name": "Invalid Currency", "currency": "GBP"}
        response = client.post("/api/v1/accounts/", json=payload)
        assert response.status_code == 422

    def test_create_account_empty_name(self, client: TestClient):
        payload = {"name": ""}
        response = client.post("/api/v1/accounts/", json=payload)
        assert response.status_code == 422

    def test_create_account_name_too_long(self, client: TestClient):
        payload = {"name": "a" * 101}
        response = client.post("/api/v1/accounts/", json=payload)
        assert response.status_code == 422

    def test_create_account_negative_balance(self, client: TestClient):
        payload = {"name": "Negative Balance", "balance": -100.0}
        response = client.post("/api/v1/accounts/", json=payload)
        assert response.status_code == 422

    def test_create_account_whitespace_handling(self, client: TestClient):
        payload = {"name": "  Trimmed Name  ", "description": "  Trimmed Description  "}
        response = client.post("/api/v1/accounts/", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Trimmed Name"
        assert data["description"] == "Trimmed Description"


class TestAccountList:
    def test_get_accounts_empty(self, client: TestClient):
        response = client.get("/api/v1/accounts/")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 100
        assert data["pages"] == 0

    def test_get_accounts_with_data(self, client: TestClient):
        accounts = [{"name": f"Account {i}", "balance": float(i * 100)} for i in range(5)]
        created_ids = []
        for account in accounts:
            response = client.post("/api/v1/accounts/", json=account)
            created_ids.append(response.json()["id"])

        response = client.get("/api/v1/accounts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 5
        assert data["pages"] == 1

    def test_get_accounts_pagination(self, client: TestClient):
        for i in range(15):
            client.post("/api/v1/accounts/", json={"name": f"Account {i}"})

        response = client.get("/api/v1/accounts/?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5
        assert data["total"] == 15
        assert data["page"] == 1
        assert data["size"] == 5
        assert data["pages"] == 3

        response = client.get("/api/v1/accounts/?skip=5&limit=5")
        data = response.json()
        assert data["page"] == 2

        response = client.get("/api/v1/accounts/?skip=10&limit=5")
        data = response.json()
        assert data["page"] == 3
        assert len(data["items"]) == 5

    def test_get_accounts_limit_validation(self, client: TestClient):
        response = client.get("/api/v1/accounts/?limit=0")
        assert response.status_code == 422

        response = client.get("/api/v1/accounts/?limit=1001")
        assert response.status_code == 422

        response = client.get("/api/v1/accounts/?skip=-1")
        assert response.status_code == 422


class TestAccountGet:
    def test_get_account_by_id(self, client: TestClient):
        create_response = client.post(
            "/api/v1/accounts/",
            json={"name": "Test Account", "balance": 500.0, "description": "Test"},
        )
        account_id = create_response.json()["id"]

        response = client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id
        assert data["name"] == "Test Account"
        assert data["balance"] == 500.0
        assert data["description"] == "Test"

    def test_get_account_not_found(self, client: TestClient):
        fake_id = 99999
        response = client.get(f"/api/v1/accounts/{fake_id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Account not found"

    def test_get_account_invalid_id(self, client: TestClient):
        response = client.get("/api/v1/accounts/invalid-id")
        assert response.status_code == 422


class TestAccountUpdate:
    def test_update_account_all_fields(self, client: TestClient):
        create_response = client.post(
            "/api/v1/accounts/",
            json={"name": "Original", "currency": "EUR", "balance": 100.0},
        )
        account_id = create_response.json()["id"]

        update_payload = {
            "name": "Updated",
            "currency": "USD",
            "balance": 200.0,
            "description": "Updated description",
        }
        response = client.patch(f"/api/v1/accounts/{account_id}", json=update_payload)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated"
        assert data["currency"] == "USD"
        assert data["balance"] == 200.0
        assert data["description"] == "Updated description"

    def test_update_account_partial(self, client: TestClient):
        create_response = client.post(
            "/api/v1/accounts/",
            json={
                "name": "Original",
                "currency": "EUR",
                "balance": 100.0,
                "description": "Original desc",
            },
        )
        account_id = create_response.json()["id"]

        response = client.patch(f"/api/v1/accounts/{account_id}", json={"name": "New Name"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name"
        assert data["currency"] == "EUR"
        assert data["balance"] == 100.0
        assert data["description"] == "Original desc"

    def test_update_account_not_found(self, client: TestClient):
        fake_id = 99999
        response = client.patch(f"/api/v1/accounts/{fake_id}", json={"name": "Updated"})
        assert response.status_code == 404

    def test_update_account_invalid_data(self, client: TestClient):
        create_response = client.post("/api/v1/accounts/", json={"name": "Test"})
        account_id = create_response.json()["id"]

        response = client.patch(f"/api/v1/accounts/{account_id}", json={"balance": -100})
        assert response.status_code == 422

        response = client.patch(f"/api/v1/accounts/{account_id}", json={"name": ""})
        assert response.status_code == 422

        response = client.patch(f"/api/v1/accounts/{account_id}", json={"currency": "INVALID"})
        assert response.status_code == 422


class TestAccountDelete:
    def test_delete_account(self, client: TestClient):
        create_response = client.post("/api/v1/accounts/", json={"name": "To Delete"})
        account_id = create_response.json()["id"]

        response = client.delete(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == account_id

        response = client.get(f"/api/v1/accounts/{account_id}")
        assert response.status_code == 404

    def test_delete_account_not_found(self, client: TestClient):
        fake_id = 99999
        response = client.delete(f"/api/v1/accounts/{fake_id}")
        assert response.status_code == 404

    def test_delete_then_list(self, client: TestClient):
        account_ids = []
        for i in range(3):
            response = client.post("/api/v1/accounts/", json={"name": f"Account {i}"})
            account_ids.append(response.json()["id"])

        client.delete(f"/api/v1/accounts/{account_ids[1]}")

        response = client.get("/api/v1/accounts/")
        data = response.json()
        assert data["total"] == 2
        remaining_ids = [item["id"] for item in data["items"]]
        assert account_ids[0] in remaining_ids
        assert account_ids[1] not in remaining_ids
        assert account_ids[2] in remaining_ids


class TestAccountIntegration:
    def test_full_crud_workflow(self, client: TestClient):
        create_payload = {
            "name": "Integration Test",
            "currency": "USD",
            "balance": 1000.0,
            "description": "Initial",
        }
        create_response = client.post("/api/v1/accounts/", json=create_payload)
        assert create_response.status_code == 200
        account_id = create_response.json()["id"]

        get_response = client.get(f"/api/v1/accounts/{account_id}")
        assert get_response.status_code == 200
        assert get_response.json()["name"] == "Integration Test"

        update_response = client.patch(
            f"/api/v1/accounts/{account_id}", json={"balance": 2000.0, "description": "Updated"}
        )
        assert update_response.status_code == 200
        assert update_response.json()["balance"] == 2000.0

        list_response = client.get("/api/v1/accounts/")
        assert len(list_response.json()["items"]) == 1

        delete_response = client.delete(f"/api/v1/accounts/{account_id}")
        assert delete_response.status_code == 200

        verify_response = client.get(f"/api/v1/accounts/{account_id}")
        assert verify_response.status_code == 404

    def test_multiple_accounts_management(self, client: TestClient):
        accounts_data = [
            {"name": "Checking", "currency": "USD", "balance": 5000.0},
            {"name": "Savings", "currency": "EUR", "balance": 10000.0},
            {"name": "Investment", "currency": "USD", "balance": 25000.0},
        ]

        created_accounts = []
        for data in accounts_data:
            response = client.post("/api/v1/accounts/", json=data)
            created_accounts.append(response.json())

        response = client.get("/api/v1/accounts/")
        assert response.json()["total"] == 3

        total_usd_balance = sum(
            acc["balance"] for acc in created_accounts if acc["currency"] == "USD"
        )
        assert total_usd_balance == 30000.0

        for account in created_accounts[:2]:
            client.delete(f"/api/v1/accounts/{account['id']}")

        response = client.get("/api/v1/accounts/")
        assert response.json()["total"] == 1
        assert response.json()["items"][0]["name"] == "Investment"
