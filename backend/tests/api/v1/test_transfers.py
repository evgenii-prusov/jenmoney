"""Tests for transfer API endpoints."""

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from jenmoney import crud, schemas
from jenmoney.main import app
from jenmoney.services.transfer_service import TransferService


client = TestClient(app)


class TestTransferCreate:
    """Test transfer creation."""

    def test_create_transfer_same_currency(self, db: Session, sample_accounts):
        """Test creating a transfer between accounts with same currency."""
        account_1, account_2 = sample_accounts
        
        # Update balances
        account_1.balance = Decimal("1000.00")
        account_2.balance = Decimal("500.00")
        db.commit()
        
        transfer_data = {
            "from_account_id": account_1.id,
            "to_account_id": account_2.id,
            "from_amount": 100.00,
            "description": "Test transfer"
        }
        
        response = client.post("/api/v1/transfers/", json=transfer_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["from_account_id"] == account_1.id
        assert data["to_account_id"] == account_2.id
        assert data["from_amount"] == 100.00
        assert data["to_amount"] == 100.00  # Same currency
        assert data["from_currency"] == "EUR"
        assert data["to_currency"] == "EUR"
        assert data["exchange_rate"] is None  # Same currency
        assert data["status"] == "completed"
        assert data["description"] == "Test transfer"
        
        # Check account balances were updated
        db.refresh(account_1)
        db.refresh(account_2)
        assert account_1.balance == Decimal("900.00")
        assert account_2.balance == Decimal("600.00")

    def test_create_transfer_insufficient_funds(self, db: Session, sample_accounts):
        """Test creating a transfer with insufficient funds."""
        account_1, account_2 = sample_accounts
        
        # Set low balance
        account_1.balance = Decimal("50.00")
        db.commit()
        
        transfer_data = {
            "from_account_id": account_1.id,
            "to_account_id": account_2.id,
            "from_amount": 100.00
        }
        
        response = client.post("/api/v1/transfers/", json=transfer_data)
        assert response.status_code == 400
        assert "Insufficient funds" in response.json()["detail"]

    def test_create_transfer_same_account(self, db: Session, sample_accounts):
        """Test creating a transfer to the same account (should fail)."""
        account_1, _ = sample_accounts
        
        transfer_data = {
            "from_account_id": account_1.id,
            "to_account_id": account_1.id,
            "from_amount": 100.00
        }
        
        response = client.post("/api/v1/transfers/", json=transfer_data)
        assert response.status_code == 422  # Validation error

    def test_create_transfer_nonexistent_account(self, db: Session, sample_accounts):
        """Test creating a transfer with nonexistent account."""
        account_1, _ = sample_accounts
        
        transfer_data = {
            "from_account_id": account_1.id,
            "to_account_id": 9999,  # Non-existent
            "from_amount": 100.00
        }
        
        response = client.post("/api/v1/transfers/", json=transfer_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_transfer_negative_amount(self, db: Session, sample_accounts):
        """Test creating a transfer with negative amount."""
        account_1, account_2 = sample_accounts
        
        transfer_data = {
            "from_account_id": account_1.id,
            "to_account_id": account_2.id,
            "from_amount": -100.00
        }
        
        response = client.post("/api/v1/transfers/", json=transfer_data)
        assert response.status_code == 422  # Validation error

    def test_create_transfer_zero_amount(self, db: Session, sample_accounts):
        """Test creating a transfer with zero amount."""
        account_1, account_2 = sample_accounts
        
        transfer_data = {
            "from_account_id": account_1.id,
            "to_account_id": account_2.id,
            "from_amount": 0.00
        }
        
        response = client.post("/api/v1/transfers/", json=transfer_data)
        assert response.status_code == 422  # Validation error


class TestTransferList:
    """Test transfer listing."""

    def test_get_transfers_empty(self, db: Session):
        """Test getting transfers when none exist."""
        response = client.get("/api/v1/transfers/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    def test_get_transfers_with_data(self, db: Session, sample_transfers):
        """Test getting transfers when data exists."""
        response = client.get("/api/v1/transfers/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == len(sample_transfers)
        assert data["total"] == len(sample_transfers)
        
        # Check transfer data
        transfer_item = data["items"][0]
        assert "id" in transfer_item
        assert "from_account_id" in transfer_item
        assert "to_account_id" in transfer_item
        assert "from_amount" in transfer_item
        assert "to_amount" in transfer_item
        assert "status" in transfer_item

    def test_get_transfers_pagination(self, db: Session, sample_transfers):
        """Test transfer pagination."""
        response = client.get("/api/v1/transfers/?skip=0&limit=2")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["items"]) == min(2, len(sample_transfers))
        assert data["total"] == len(sample_transfers)
        assert data["page"] == 1
        assert data["size"] == 2

    def test_get_transfers_by_account(self, db: Session, sample_transfers):
        """Test filtering transfers by account ID."""
        # Get first transfer to know an account ID
        first_transfer = sample_transfers[0]
        account_id = first_transfer.from_account_id
        
        response = client.get(f"/api/v1/transfers/?account_id={account_id}")
        assert response.status_code == 200
        
        data = response.json()
        # Should include transfers where account is either source or destination
        for item in data["items"]:
            assert item["from_account_id"] == account_id or item["to_account_id"] == account_id


class TestTransferGet:
    """Test getting individual transfers."""

    def test_get_transfer_by_id(self, db: Session, sample_transfers):
        """Test getting a transfer by ID."""
        transfer = sample_transfers[0]
        
        response = client.get(f"/api/v1/transfers/{transfer.id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == transfer.id
        assert data["from_account_id"] == transfer.from_account_id
        assert data["to_account_id"] == transfer.to_account_id

    def test_get_transfer_not_found(self, db: Session):
        """Test getting a non-existent transfer."""
        response = client.get("/api/v1/transfers/9999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestTransferUpdate:
    """Test transfer updates."""

    def test_update_transfer_description(self, db: Session, sample_transfers):
        """Test updating transfer description."""
        transfer = sample_transfers[0]
        
        update_data = {
            "description": "Updated description"
        }
        
        response = client.patch(f"/api/v1/transfers/{transfer.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["description"] == "Updated description"

    def test_update_transfer_status(self, db: Session, sample_transfers):
        """Test updating transfer status."""
        # Create a pending transfer first
        transfer_service = TransferService(db)
        transfer = sample_transfers[0]
        transfer.status = "pending"
        db.commit()
        
        update_data = {
            "status": "cancelled"
        }
        
        response = client.patch(f"/api/v1/transfers/{transfer.id}", json=update_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "cancelled"

    def test_update_transfer_not_found(self, db: Session):
        """Test updating a non-existent transfer."""
        update_data = {
            "description": "Updated description"
        }
        
        response = client.patch("/api/v1/transfers/9999", json=update_data)
        assert response.status_code == 404


class TestTransferIntegration:
    """Integration tests for transfers."""

    def test_transfer_workflow(self, db: Session, sample_accounts):
        """Test complete transfer workflow."""
        account_1, account_2 = sample_accounts
        
        # Set initial balances
        account_1.balance = Decimal("1000.00")
        account_2.balance = Decimal("500.00")
        db.commit()
        
        # Create transfer
        transfer_data = {
            "from_account_id": account_1.id,
            "to_account_id": account_2.id,
            "from_amount": 250.00,
            "description": "Test transfer"
        }
        
        create_response = client.post("/api/v1/transfers/", json=transfer_data)
        assert create_response.status_code == 200
        transfer_id = create_response.json()["id"]
        
        # Verify balances
        db.refresh(account_1)
        db.refresh(account_2)
        assert account_1.balance == Decimal("750.00")
        assert account_2.balance == Decimal("750.00")
        
        # Get transfer
        get_response = client.get(f"/api/v1/transfers/{transfer_id}")
        assert get_response.status_code == 200
        assert get_response.json()["from_amount"] == 250.00
        
        # List transfers
        list_response = client.get("/api/v1/transfers/")
        assert list_response.status_code == 200
        assert any(item["id"] == transfer_id for item in list_response.json()["items"])
        
        # Update transfer
        update_data = {"description": "Updated test transfer"}
        update_response = client.patch(f"/api/v1/transfers/{transfer_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["description"] == "Updated test transfer"