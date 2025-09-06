import pytest
from fastapi.testclient import TestClient


class TestBudgetIncomeExpenseCalculation:
    """Test budget functionality with both income and expense categories."""
    
    def test_income_budget_calculation_with_transactions(self, client: TestClient) -> None:
        """Test that income budget calculations work correctly with income transactions."""
        # Create income category
        category_data = {
            "name": "Salary",
            "description": "Monthly salary",
            "type": "income"
        }
        category_response = client.post("/api/v1/categories/", json=category_data)
        assert category_response.status_code == 200
        category = category_response.json()
        
        # Create account for transactions
        account_data = {
            "name": "Checking Account",
            "balance": "0.00",
            "currency": "USD"
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        assert account_response.status_code == 200
        account = account_response.json()
        
        # Create income budget
        budget_data = {
            "budget_year": 2025,
            "budget_month": 1,
            "category_id": category["id"],
            "planned_amount": "3000.00",
            "currency": "USD"
        }
        budget_response = client.post("/api/v1/budgets/", json=budget_data)
        assert budget_response.status_code == 200
        budget = budget_response.json()
        assert budget["actual_amount"] == "0.00"
        
        # Create income transaction (positive amount)
        transaction_data = {
            "account_id": account["id"],
            "category_id": category["id"],
            "amount": "2500.00",  # Positive for income
            "description": "Salary payment",
            "transaction_date": "2025-01-15"
        }
        transaction_response = client.post("/api/v1/transactions/", json=transaction_data)
        assert transaction_response.status_code == 200
        
        # Get budget again - should now show actual income amount
        budget_response = client.get(f"/api/v1/budgets/{budget['id']}")
        assert budget_response.status_code == 200
        updated_budget = budget_response.json()
        assert updated_budget["actual_amount"] == "2500.00"
        
        # Create another income transaction
        transaction_data2 = {
            "account_id": account["id"],
            "category_id": category["id"],
            "amount": "300.00",  # Bonus payment
            "description": "Bonus payment",
            "transaction_date": "2025-01-20"
        }
        transaction_response2 = client.post("/api/v1/transactions/", json=transaction_data2)
        assert transaction_response2.status_code == 200
        
        # Get budget again - should show combined income
        budget_response = client.get(f"/api/v1/budgets/{budget['id']}")
        assert budget_response.status_code == 200
        final_budget = budget_response.json()
        assert final_budget["actual_amount"] == "2800.00"  # 2500 + 300
        
    def test_expense_budget_calculation_with_transactions(self, client: TestClient) -> None:
        """Test that expense budget calculations work correctly with expense transactions."""
        # Create expense category
        category_data = {
            "name": "Groceries",
            "description": "Food expenses",
            "type": "expense"
        }
        category_response = client.post("/api/v1/categories/", json=category_data)
        assert category_response.status_code == 200
        category = category_response.json()
        
        # Create account for transactions
        account_data = {
            "name": "Checking Account",
            "balance": "1000.00",
            "currency": "USD"
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        assert account_response.status_code == 200
        account = account_response.json()
        
        # Create expense budget
        budget_data = {
            "budget_year": 2025,
            "budget_month": 1,
            "category_id": category["id"],
            "planned_amount": "400.00",
            "currency": "USD"
        }
        budget_response = client.post("/api/v1/budgets/", json=budget_data)
        assert budget_response.status_code == 200
        budget = budget_response.json()
        assert budget["actual_amount"] == "0.00"
        
        # Create expense transaction (negative amount)
        transaction_data = {
            "account_id": account["id"],
            "category_id": category["id"],
            "amount": "-150.00",  # Negative for expense
            "description": "Grocery shopping",
            "transaction_date": "2025-01-10"
        }
        transaction_response = client.post("/api/v1/transactions/", json=transaction_data)
        assert transaction_response.status_code == 200
        
        # Get budget again - should now show actual expense amount
        budget_response = client.get(f"/api/v1/budgets/{budget['id']}")
        assert budget_response.status_code == 200
        updated_budget = budget_response.json()
        assert updated_budget["actual_amount"] == "150.00"  # Absolute value
        
        # Create another expense transaction
        transaction_data2 = {
            "account_id": account["id"],
            "category_id": category["id"],
            "amount": "-75.00",
            "description": "More groceries",
            "transaction_date": "2025-01-20"
        }
        transaction_response2 = client.post("/api/v1/transactions/", json=transaction_data2)
        assert transaction_response2.status_code == 200
        
        # Get budget again - should show combined expenses
        budget_response = client.get(f"/api/v1/budgets/{budget['id']}")
        assert budget_response.status_code == 200
        final_budget = budget_response.json()
        assert final_budget["actual_amount"] == "225.00"  # 150 + 75
        
    def test_mixed_income_expense_budget_list(self, client: TestClient) -> None:
        """Test budget list with both income and expense categories."""
        # Create income category
        income_category_data = {
            "name": "Freelance",
            "description": "Freelance income",
            "type": "income"
        }
        income_response = client.post("/api/v1/categories/", json=income_category_data)
        assert income_response.status_code == 200
        income_category = income_response.json()
        
        # Create expense category
        expense_category_data = {
            "name": "Transportation",
            "description": "Transport costs",
            "type": "expense"
        }
        expense_response = client.post("/api/v1/categories/", json=expense_category_data)
        assert expense_response.status_code == 200
        expense_category = expense_response.json()
        
        # Create account
        account_data = {
            "name": "Main Account",
            "balance": "500.00",
            "currency": "USD"
        }
        account_response = client.post("/api/v1/accounts/", json=account_data)
        assert account_response.status_code == 200
        account = account_response.json()
        
        # Create income budget
        income_budget_data = {
            "budget_year": 2025,
            "budget_month": 2,
            "category_id": income_category["id"],
            "planned_amount": "1500.00",
            "currency": "USD"
        }
        income_budget_response = client.post("/api/v1/budgets/", json=income_budget_data)
        assert income_budget_response.status_code == 200
        
        # Create expense budget
        expense_budget_data = {
            "budget_year": 2025,
            "budget_month": 2,
            "category_id": expense_category["id"],
            "planned_amount": "200.00",
            "currency": "USD"
        }
        expense_budget_response = client.post("/api/v1/budgets/", json=expense_budget_data)
        assert expense_budget_response.status_code == 200
        
        # Create income transaction
        income_transaction_data = {
            "account_id": account["id"],
            "category_id": income_category["id"],
            "amount": "1200.00",
            "description": "Freelance payment",
            "transaction_date": "2025-02-10"
        }
        client.post("/api/v1/transactions/", json=income_transaction_data)
        
        # Create expense transaction
        expense_transaction_data = {
            "account_id": account["id"],
            "category_id": expense_category["id"],
            "amount": "-120.00",
            "description": "Bus pass",
            "transaction_date": "2025-02-05"
        }
        client.post("/api/v1/transactions/", json=expense_transaction_data)
        
        # Get budget list
        list_response = client.get("/api/v1/budgets/?year=2025&month=2")
        assert list_response.status_code == 200
        data = list_response.json()
        
        assert len(data["items"]) == 2
        assert data["summary"]["total_planned"] == "1700.00"  # 1500 + 200
        assert data["summary"]["total_actual"] == "1320.00"   # 1200 + 120
        
        # Check individual budget amounts
        budgets_by_category = {item["category"]["name"]: item for item in data["items"]}
        assert budgets_by_category["Freelance"]["actual_amount"] == "1200.00"
        assert budgets_by_category["Transportation"]["actual_amount"] == "120.00"