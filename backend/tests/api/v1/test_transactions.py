import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session

from jenmoney.models.account import Account
from jenmoney.models.category import Category, CategoryType
from jenmoney.schemas.transaction import TransactionCreate, TransactionUpdate


class TestTransactionCreate:
    """Test transaction creation."""

    def test_create_transaction_with_all_fields(self, client, db_session: Session):
        """Test creating a transaction with all fields."""
        # Create account
        account = Account(name="Test Account", currency="USD", balance=Decimal("1000.00"))
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        # Create category
        category = Category(name="Test Category", type=CategoryType.expense)
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        transaction_data = {
            "account_id": account.id,
            "amount": -50.00,  # Expense
            "category_id": category.id,
            "description": "Test expense transaction",
            "transaction_date": "2025-01-15"
        }

        response = client.post("/api/v1/transactions/", json=transaction_data)
        assert response.status_code == 200

        data = response.json()
        assert data["account_id"] == account.id
        assert data["amount"] == -50.00
        assert data["currency"] == "USD"
        assert data["category_id"] == category.id
        assert data["description"] == "Test expense transaction"
        assert data["transaction_date"] == "2025-01-15"

        # Check that account balance was updated
        db_session.refresh(account)
        assert account.balance == Decimal("950.00")  # 1000 - 50

    def test_create_transaction_income(self, client, db_session: Session):
        """Test creating an income transaction."""
        # Create account
        account = Account(name="Test Account", currency="EUR", balance=Decimal("500.00"))
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        transaction_data = {
            "account_id": account.id,
            "amount": 200.00,  # Income
            "description": "Salary payment"
        }

        response = client.post("/api/v1/transactions/", json=transaction_data)
        assert response.status_code == 200

        data = response.json()
        assert data["account_id"] == account.id
        assert data["amount"] == 200.00
        assert data["currency"] == "EUR"
        assert data["category_id"] is None

        # Check that account balance was updated
        db_session.refresh(account)
        assert account.balance == Decimal("700.00")  # 500 + 200

    def test_create_transaction_without_category(self, client, db_session: Session):
        """Test creating a transaction without category."""
        # Create account
        account = Account(name="Test Account", currency="USD", balance=Decimal("1000.00"))
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        transaction_data = {
            "account_id": account.id,
            "amount": -25.50,
            "description": "Quick expense"
        }

        response = client.post("/api/v1/transactions/", json=transaction_data)
        assert response.status_code == 200

        data = response.json()
        assert data["category_id"] is None
        assert data["amount"] == -25.50

    def test_create_transaction_invalid_account(self, client):
        """Test creating a transaction with invalid account."""
        transaction_data = {
            "account_id": 999,
            "amount": -50.00,
            "description": "Test transaction"
        }

        response = client.post("/api/v1/transactions/", json=transaction_data)
        assert response.status_code == 404
        assert "Account 999 not found" in response.json()["detail"]

    def test_create_transaction_invalid_category(self, client, db_session: Session):
        """Test creating a transaction with invalid category."""
        # Create account
        account = Account(name="Test Account", currency="USD", balance=Decimal("1000.00"))
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        transaction_data = {
            "account_id": account.id,
            "amount": -50.00,
            "category_id": 999,
            "description": "Test transaction"
        }

        response = client.post("/api/v1/transactions/", json=transaction_data)
        assert response.status_code == 404
        assert "Category 999 not found" in response.json()["detail"]


class TestTransactionList:
    """Test transaction listing."""

    def test_get_transactions_empty(self, client):
        """Test getting transactions when none exist."""
        response = client.get("/api/v1/transactions/")
        assert response.status_code == 200

        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1
        assert data["size"] == 10

    def test_get_transactions_with_data(self, client, db_session: Session):
        """Test getting transactions with data."""
        # Create accounts
        account1 = Account(name="Account 1", currency="USD", balance=Decimal("1000.00"))
        account2 = Account(name="Account 2", currency="EUR", balance=Decimal("500.00"))
        db_session.add_all([account1, account2])
        db_session.commit()

        # Create transactions via API
        transaction_data_1 = {
            "account_id": account1.id,
            "amount": -100.00,
            "description": "Expense 1"
        }
        transaction_data_2 = {
            "account_id": account2.id,
            "amount": 50.00,
            "description": "Income 1"
        }

        client.post("/api/v1/transactions/", json=transaction_data_1)
        client.post("/api/v1/transactions/", json=transaction_data_2)

        # Get all transactions
        response = client.get("/api/v1/transactions/")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 2

    def test_get_transactions_by_account(self, client, db_session: Session):
        """Test filtering transactions by account."""
        # Create accounts
        account1 = Account(name="Account 1", currency="USD", balance=Decimal("1000.00"))
        account2 = Account(name="Account 2", currency="EUR", balance=Decimal("500.00"))
        db_session.add_all([account1, account2])
        db_session.commit()

        # Create transactions
        transaction_data_1 = {
            "account_id": account1.id,
            "amount": -100.00,
            "description": "Expense 1"
        }
        transaction_data_2 = {
            "account_id": account2.id,
            "amount": 50.00,
            "description": "Income 1"
        }

        client.post("/api/v1/transactions/", json=transaction_data_1)
        client.post("/api/v1/transactions/", json=transaction_data_2)

        # Filter by account1
        response = client.get(f"/api/v1/transactions/?account_id={account1.id}")
        assert response.status_code == 200

        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["account_id"] == account1.id
        assert data["total"] == 1


class TestTransactionUpdate:
    """Test transaction updates."""

    def test_update_transaction_amount(self, client, db_session: Session):
        """Test updating transaction amount with balance adjustments."""
        # Create account
        account = Account(name="Test Account", currency="USD", balance=Decimal("1000.00"))
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        # Create transaction
        transaction_data = {
            "account_id": account.id,
            "amount": -100.00,
            "description": "Original expense"
        }

        create_response = client.post("/api/v1/transactions/", json=transaction_data)
        assert create_response.status_code == 200
        transaction_id = create_response.json()["id"]

        # Verify account balance after creation
        db_session.refresh(account)
        assert account.balance == Decimal("900.00")  # 1000 - 100

        # Update transaction amount
        update_data = {
            "amount": -150.00  # Increased expense
        }

        update_response = client.patch(f"/api/v1/transactions/{transaction_id}", json=update_data)
        assert update_response.status_code == 200

        # Verify account balance was adjusted
        db_session.refresh(account)
        assert account.balance == Decimal("850.00")  # 1000 - 150

    def test_update_transaction_description(self, client, db_session: Session):
        """Test updating transaction description."""
        # Create account
        account = Account(name="Test Account", currency="USD", balance=Decimal("1000.00"))
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        # Create transaction
        transaction_data = {
            "account_id": account.id,
            "amount": -50.00,
            "description": "Original description"
        }

        create_response = client.post("/api/v1/transactions/", json=transaction_data)
        assert create_response.status_code == 200
        transaction_id = create_response.json()["id"]

        # Update description only
        update_data = {
            "description": "Updated description"
        }

        update_response = client.patch(f"/api/v1/transactions/{transaction_id}", json=update_data)
        assert update_response.status_code == 200

        data = update_response.json()
        assert data["description"] == "Updated description"
        assert data["amount"] == -50.00  # Amount unchanged

        # Verify account balance unchanged
        db_session.refresh(account)
        assert account.balance == Decimal("950.00")  # 1000 - 50, unchanged

    def test_update_transaction_not_found(self, client):
        """Test updating a non-existent transaction."""
        update_data = {
            "description": "Updated description"
        }

        response = client.patch("/api/v1/transactions/999", json=update_data)
        assert response.status_code == 404
        assert "Transaction 999 not found" in response.json()["detail"]


class TestTransactionDelete:
    """Test transaction deletion."""

    def test_delete_transaction_balances_updated(self, client, db_session: Session):
        """Test that deleting a transaction correctly reverses account balance changes."""
        # Create account
        account = Account(name="Test Account", currency="USD", balance=Decimal("1000.00"))
        db_session.add(account)
        db_session.commit()
        db_session.refresh(account)

        # Create transaction
        transaction_data = {
            "account_id": account.id,
            "amount": -250.00,
            "description": "Test expense for deletion"
        }

        create_response = client.post("/api/v1/transactions/", json=transaction_data)
        assert create_response.status_code == 200
        transaction_id = create_response.json()["id"]

        # Verify balance changed after creation
        db_session.refresh(account)
        assert account.balance == Decimal("750.00")  # 1000 - 250

        # Delete transaction
        delete_response = client.delete(f"/api/v1/transactions/{transaction_id}")
        assert delete_response.status_code == 200

        # Verify balance was restored
        db_session.refresh(account)
        assert account.balance == Decimal("1000.00")  # Back to original

    def test_delete_transaction_not_found(self, client):
        """Test deleting a non-existent transaction."""
        response = client.delete("/api/v1/transactions/999")
        assert response.status_code == 404
        assert "Transaction 999 not found" in response.json()["detail"]


class TestTransactionIntegration:
    """Test transaction workflow."""

    def test_transaction_workflow(self, client, db_session: Session):
        """Test full transaction workflow: create, read, update, delete."""
        # Create account and category
        account = Account(name="Test Account", currency="USD", balance=Decimal("1000.00"))
        category = Category(name="Food", type=CategoryType.expense)
        db_session.add_all([account, category])
        db_session.commit()

        # 1. Create transaction
        transaction_data = {
            "account_id": account.id,
            "amount": -75.50,
            "category_id": category.id,
            "description": "Grocery shopping"
        }

        create_response = client.post("/api/v1/transactions/", json=transaction_data)
        assert create_response.status_code == 200
        transaction_id = create_response.json()["id"]

        # 2. Read transaction
        get_response = client.get(f"/api/v1/transactions/{transaction_id}")
        assert get_response.status_code == 200
        assert get_response.json()["description"] == "Grocery shopping"

        # 3. Update transaction
        update_data = {"amount": -85.50}
        update_response = client.patch(f"/api/v1/transactions/{transaction_id}", json=update_data)
        assert update_response.status_code == 200

        # 4. List transactions
        list_response = client.get("/api/v1/transactions/")
        assert list_response.status_code == 200
        assert len(list_response.json()["items"]) == 1

        # 5. Delete transaction
        delete_response = client.delete(f"/api/v1/transactions/{transaction_id}")
        assert delete_response.status_code == 200

        # 6. Verify deletion
        get_after_delete = client.get(f"/api/v1/transactions/{transaction_id}")
        assert get_after_delete.status_code == 404