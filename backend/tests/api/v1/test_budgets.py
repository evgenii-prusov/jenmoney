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
        assert data["actual_amount"] == "0.00"  # No transactions yet
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_budget_for_income_category_succeeds(self, client: TestClient) -> None:
        # Create income category
        category_data = {
            "name": "Salary",
            "description": "Monthly salary",
            "type": "income"
        }
        category_response = client.post("/api/v1/categories/", json=category_data)
        assert category_response.status_code == 200
        category = category_response.json()
        
        # Create budget for income category (should now succeed)
        budget_data = {
            "budget_year": 2025,
            "budget_month": 1,
            "category_id": category["id"],
            "planned_amount": "1000.00",
            "currency": "USD"
        }
        response = client.post("/api/v1/budgets/", json=budget_data)
        assert response.status_code == 200
        data = response.json()
        assert data["budget_year"] == 2025
        assert data["budget_month"] == 1
        assert data["category_id"] == category["id"]
        assert data["planned_amount"] == "1000.00"
        assert data["currency"] == "USD"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

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

    def test_create_budget_uses_default_currency_when_none_provided(self, client: TestClient) -> None:
        # First set the default currency to EUR
        settings_response = client.patch("/api/v1/settings/", json={"default_currency": "EUR"})
        assert settings_response.status_code == 200
        
        # Create a category for budgeting
        category_data = {
            "name": "Travel",
            "description": "Travel expenses", 
            "type": "expense"
        }
        category_response = client.post("/api/v1/categories/", json=category_data)
        assert category_response.status_code == 200
        category = category_response.json()
        
        # Create budget without specifying currency (should use default EUR)
        budget_data = {
            "budget_year": 2025,
            "budget_month": 4,
            "category_id": category["id"],
            "planned_amount": "1000.00"
            # Note: no currency field
        }
        response = client.post("/api/v1/budgets/", json=budget_data)
        assert response.status_code == 200
        data = response.json()
        
        # Should use the default currency (EUR)
        assert data["currency"] == "EUR"
        assert data["planned_amount"] == "1000.00"
        
        # Reset default currency back to USD for other tests
        client.patch("/api/v1/settings/", json={"default_currency": "USD"})


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


class TestBudgetChildCategoryAggregation:
    def test_budget_aggregates_child_category_expenses(self, client: TestClient) -> None:
        """Test that budget for parent category includes expenses from child categories."""
        # Create parent category
        parent_category_data = {
            "name": "Питание",  # Food
            "description": "Food expenses",
            "type": "expense"
        }
        parent_response = client.post("/api/v1/categories/", json=parent_category_data)
        assert parent_response.status_code == 200
        parent_category = parent_response.json()
        
        # Create child categories
        child1_data = {
            "name": "Рестораны",  # Restaurants
            "description": "Restaurant expenses",
            "type": "expense",
            "parent_id": parent_category["id"]
        }
        child1_response = client.post("/api/v1/categories/", json=child1_data)
        assert child1_response.status_code == 200
        child1_category = child1_response.json()
        
        child2_data = {
            "name": "Продукты",  # Groceries
            "description": "Grocery expenses",
            "type": "expense",
            "parent_id": parent_category["id"]
        }
        child2_response = client.post("/api/v1/categories/", json=child2_data)
        assert child2_response.status_code == 200
        child2_category = child2_response.json()
        
        # Create an account for transactions
        account_data = {
            "name": "Test Account",
            "balance": "1000.00",
            "currency": "USD"
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        assert account_response.status_code == 200
        account = account_response.json()
        
        # Create transactions in child categories
        transaction1_data = {
            "account_id": account["id"],
            "amount": "-50.00",  # Restaurant expense
            "currency": "USD",
            "category_id": child1_category["id"],
            "description": "Restaurant dinner",
            "transaction_date": "2025-01-15"
        }
        transaction1_response = client.post("/api/v1/transactions/", json=transaction1_data)
        assert transaction1_response.status_code == 200
        
        transaction2_data = {
            "account_id": account["id"],
            "amount": "-30.00",  # Grocery expense
            "currency": "USD",
            "category_id": child2_category["id"],
            "description": "Weekly groceries",
            "transaction_date": "2025-01-20"
        }
        transaction2_response = client.post("/api/v1/transactions/", json=transaction2_data)
        assert transaction2_response.status_code == 200
        
        # Create transaction directly in parent category
        transaction3_data = {
            "account_id": account["id"],
            "amount": "-20.00",  # Direct parent expense
            "currency": "USD",
            "category_id": parent_category["id"],
            "description": "Food delivery",
            "transaction_date": "2025-01-25"
        }
        transaction3_response = client.post("/api/v1/transactions/", json=transaction3_data)
        assert transaction3_response.status_code == 200
        
        # Create budget for parent category
        budget_data = {
            "budget_year": 2025,
            "budget_month": 1,
            "category_id": parent_category["id"],
            "planned_amount": "200.00",
            "currency": "USD"
        }
        budget_response = client.post("/api/v1/budgets/", json=budget_data)
        assert budget_response.status_code == 200
        budget = budget_response.json()
        
        # Verify that actual_amount includes all expenses (50 + 30 + 20 = 100)
        assert budget["actual_amount"] == "100.00"
        assert budget["planned_amount"] == "200.00"
        
        # Also test via budget list endpoint
        list_response = client.get("/api/v1/budgets/?year=2025&month=1")
        assert list_response.status_code == 200
        list_data = list_response.json()
        
        assert len(list_data["items"]) == 1
        budget_item = list_data["items"][0]
        assert budget_item["actual_amount"] == "100.00"
        assert list_data["summary"]["total_actual"] == "100.00"
        
    def test_budget_child_categories_two_levels(self, client: TestClient) -> None:
        """Test budget aggregation with 2 levels of nested categories (API limit)."""
        # Create parent category
        parent_data = {"name": "Transport", "type": "expense"}
        parent_response = client.post("/api/v1/categories/", json=parent_data)
        assert parent_response.status_code == 200
        parent_category = parent_response.json()
        
        # Create child categories (API allows max 2 levels)
        child1_data = {
            "name": "Car",
            "type": "expense",
            "parent_id": parent_category["id"]
        }
        child1_response = client.post("/api/v1/categories/", json=child1_data)
        assert child1_response.status_code == 200
        child1_category = child1_response.json()
        
        child2_data = {
            "name": "Public Transport",
            "type": "expense",
            "parent_id": parent_category["id"]
        }
        child2_response = client.post("/api/v1/categories/", json=child2_data)
        assert child2_response.status_code == 200
        child2_category = child2_response.json()
        
        # Create account
        account_data = {"name": "Test Account", "balance": "500.00", "currency": "USD"}
        account_response = client.post("/api/v1/accounts/", json=account_data)
        assert account_response.status_code == 200
        account = account_response.json()
        
        # Create transactions in child categories
        trans_child1_data = {
            "account_id": account["id"],
            "amount": "-60.00",
            "currency": "USD",
            "category_id": child1_category["id"],
            "description": "Car fuel",
            "transaction_date": "2025-02-10"
        }
        trans_child1_response = client.post("/api/v1/transactions/", json=trans_child1_data)
        assert trans_child1_response.status_code == 200
        
        trans_child2_data = {
            "account_id": account["id"],
            "amount": "-15.00",
            "currency": "USD",
            "category_id": child2_category["id"],
            "description": "Bus ticket",
            "transaction_date": "2025-02-15"
        }
        trans_child2_response = client.post("/api/v1/transactions/", json=trans_child2_data)
        assert trans_child2_response.status_code == 200
        
        # Create budget for parent category
        budget_data = {
            "budget_year": 2025,
            "budget_month": 2,
            "category_id": parent_category["id"],
            "planned_amount": "150.00",
            "currency": "USD"
        }
        budget_response = client.post("/api/v1/budgets/", json=budget_data)
        assert budget_response.status_code == 200
        budget = budget_response.json()
        
        # Should aggregate all child expenses (60 + 15 = 75)
        assert budget["actual_amount"] == "75.00"


class TestBudgetCurrencyConversion:
    """Test that budget summary displays amounts in user's default currency."""
    
    def test_budget_summary_uses_default_currency(self, client: TestClient) -> None:
        """Test that budget summary totals are converted to user's default currency."""
        # Set user's default currency to RUB
        response = client.patch("/api/v1/settings/", json={"default_currency": "RUB"})
        assert response.status_code == 200
        
        # Create a category
        category_response = client.post("/api/v1/categories/", json={
            "name": "Test Category",
            "type": "expense",
            "description": "Test category for budget"
        })
        assert category_response.status_code == 200
        category_id = category_response.json()["id"]
        
        # Create a budget in EUR
        budget_response = client.post("/api/v1/budgets/", json={
            "budget_year": 2025,
            "budget_month": 3,
            "category_id": category_id,
            "planned_amount": "100.00",
            "currency": "EUR"
        })
        assert budget_response.status_code == 200
        
        # Get budgets for the month
        budgets_response = client.get("/api/v1/budgets/?year=2025&month=3")
        assert budgets_response.status_code == 200
        
        data = budgets_response.json()
        summary = data["summary"]
        
        # Verify summary currency is RUB (user's default), not EUR (budget's currency)
        assert summary["currency"] == "RUB"
        
        # Verify the amount has been converted (should be much larger than 100 when converted to RUB)
        from decimal import Decimal
        total_planned = Decimal(summary["total_planned"])
        assert total_planned > Decimal("1000")  # EUR to RUB conversion should be ~90x
        
        # Verify individual budget item still shows original currency
        budget_item = data["items"][0]
        assert budget_item["currency"] == "EUR"
        assert budget_item["planned_amount"] == "100.00"
        
        # Verify new income/expense breakdown in summary
        assert "income_planned" in summary
        assert "income_actual" in summary  
        assert "expense_planned" in summary
        assert "expense_actual" in summary
        
        # Since we created an expense category, expense_planned should equal total_planned
        expense_planned = Decimal(summary["expense_planned"])
        assert expense_planned == total_planned
        
        # Income should be zero since we only created expense budgets
        income_planned = Decimal(summary["income_planned"])
        assert income_planned == Decimal("0.00")

    def test_budget_summary_separates_income_and_expense(self, client: TestClient) -> None:
        """Test that budget summary correctly separates income and expense totals."""
        # Set user's default currency to EUR for easier calculations
        response = client.patch("/api/v1/settings/", json={"default_currency": "EUR"})
        assert response.status_code == 200
        
        # Create income category
        income_category_response = client.post("/api/v1/categories/", json={
            "name": "Salary",
            "type": "income",
            "description": "Income category"
        })
        assert income_category_response.status_code == 200
        income_category_id = income_category_response.json()["id"]
        
        # Create expense category  
        expense_category_response = client.post("/api/v1/categories/", json={
            "name": "Food",
            "type": "expense", 
            "description": "Expense category"
        })
        assert expense_category_response.status_code == 200
        expense_category_id = expense_category_response.json()["id"]
        
        # Create income budget in USD (should be converted to EUR)
        income_budget_response = client.post("/api/v1/budgets/", json={
            "budget_year": 2025,
            "budget_month": 4,
            "category_id": income_category_id,
            "planned_amount": "1000.00",
            "currency": "USD"
        })
        assert income_budget_response.status_code == 200
        
        # Create expense budget in EUR
        expense_budget_response = client.post("/api/v1/budgets/", json={
            "budget_year": 2025,
            "budget_month": 4, 
            "category_id": expense_category_id,
            "planned_amount": "500.00",
            "currency": "EUR"
        })
        assert expense_budget_response.status_code == 200
        
        # Get budgets for the month
        budgets_response = client.get("/api/v1/budgets/?year=2025&month=4")
        assert budgets_response.status_code == 200
        
        data = budgets_response.json()
        summary = data["summary"]
        
        # Verify summary is in user's default currency (EUR)
        assert summary["currency"] == "EUR"
        
        # Verify income and expense are properly separated and converted
        from decimal import Decimal
        income_planned = Decimal(summary["income_planned"])
        expense_planned = Decimal(summary["expense_planned"])
        total_planned = Decimal(summary["total_planned"])
        
        # Income should be converted from USD to EUR (roughly 1000 * 0.85 = 850)
        assert income_planned > Decimal("800")  # USD to EUR conversion
        assert income_planned < Decimal("1000")  # Should be less than original USD amount
        
        # Expense should remain 500 EUR (no conversion needed)
        assert expense_planned == Decimal("500.00")
        
        # Total should be sum of converted amounts
        assert total_planned == income_planned + expense_planned