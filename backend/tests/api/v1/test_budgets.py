import pytest
from fastapi.testclient import TestClient


class TestBudgetCreate:
    def test_create_budget_with_valid_data(self, client: TestClient) -> None:
        # First create a category for budgeting
        category_data = {
            "name": "Food & Dining",
            "description": "Food expenses",
            "type": "expense"
        }
        category_response = client.post("/api/v1/categories/", json=category_data)
        assert category_response.status_code == 200
        category = category_response.json()
        
        # Create budget for this category
        budget_data = {
            "budget_year": 2025,
            "budget_month": 1,
            "category_id": category["id"],
            "planned_amount": "500.00",
            "currency": "USD"
        }
        response = client.post("/api/v1/budgets/", json=budget_data)
        assert response.status_code == 200
        data = response.json()
        assert data["budget_year"] == budget_data["budget_year"]
        assert data["budget_month"] == budget_data["budget_month"] 
        assert data["category_id"] == budget_data["category_id"]
        assert data["planned_amount"] == budget_data["planned_amount"]
        assert data["currency"] == budget_data["currency"]
        assert data["actual_amount"] == "0"  # No transactions yet
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_budget_for_income_category_fails(self, client: TestClient) -> None:
        # Create income category
        category_data = {
            "name": "Salary",
            "description": "Monthly salary",
            "type": "income"
        }
        category_response = client.post("/api/v1/categories/", json=category_data)
        assert category_response.status_code == 200
        category = category_response.json()
        
        # Try to create budget for income category (should fail)
        budget_data = {
            "budget_year": 2025,
            "budget_month": 1,
            "category_id": category["id"],
            "planned_amount": "1000.00",
            "currency": "USD"
        }
        response = client.post("/api/v1/budgets/", json=budget_data)
        assert response.status_code == 400
        assert "Budget can only be created for expense categories" in response.json()["detail"]

    def test_create_duplicate_budget_fails(self, client: TestClient) -> None:
        # Create category
        category_data = {
            "name": "Transportation",
            "type": "expense"
        }
        category_response = client.post("/api/v1/categories/", json=category_data)
        category = category_response.json()
        
        # Create first budget
        budget_data = {
            "budget_year": 2025,
            "budget_month": 2,
            "category_id": category["id"],
            "planned_amount": "200.00"
        }
        response1 = client.post("/api/v1/budgets/", json=budget_data)
        assert response1.status_code == 200
        
        # Try to create duplicate budget (same category, year, month)
        response2 = client.post("/api/v1/budgets/", json=budget_data)
        assert response2.status_code == 400
        assert "Budget already exists" in response2.json()["detail"]


class TestBudgetList:
    def test_get_budgets_for_month(self, client: TestClient) -> None:
        # Create categories and budgets
        categories = []
        for name in ["Food", "Transport", "Entertainment"]:
            cat_response = client.post("/api/v1/categories/", json={"name": name, "type": "expense"})
            categories.append(cat_response.json())
        
        # Create budgets for March 2025
        budget_data = [
            {"budget_year": 2025, "budget_month": 3, "category_id": categories[0]["id"], "planned_amount": "500.00"},
            {"budget_year": 2025, "budget_month": 3, "category_id": categories[1]["id"], "planned_amount": "300.00"},
            {"budget_year": 2025, "budget_month": 3, "category_id": categories[2]["id"], "planned_amount": "200.00"},
        ]
        
        for budget in budget_data:
            response = client.post("/api/v1/budgets/", json=budget)
            assert response.status_code == 200
        
        # Get budgets for March 2025
        response = client.get("/api/v1/budgets/?year=2025&month=3")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 3
        assert data["total"] == 3
        assert data["summary"]["budget_year"] == 2025
        assert data["summary"]["budget_month"] == 3
        assert data["summary"]["total_planned"] == "1000.00"
        assert data["summary"]["total_actual"] == "0.00"
        assert data["summary"]["categories_count"] == 3

    def test_get_budgets_empty_month(self, client: TestClient) -> None:
        # Get budgets for a month with no budgets
        response = client.get("/api/v1/budgets/?year=2025&month=12")
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) == 0
        assert data["total"] == 0
        assert data["summary"]["total_planned"] == "0.00"
        assert data["summary"]["total_actual"] == "0.00"
        assert data["summary"]["categories_count"] == 0