from decimal import Decimal
from sqlalchemy.orm import Session

from jenmoney import crud, models
from jenmoney.exceptions import InvalidAccountError
from jenmoney.schemas.transaction import TransactionCreate, TransactionUpdate


class TransactionService:
    """Service for handling transactions on accounts."""

    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, *, transaction_in: TransactionCreate) -> models.Transaction:
        """Create a new transaction and update account balance.

        Args:
            transaction_in: Transaction creation data

        Returns:
            Created transaction object

        Raises:
            InvalidAccountError: If account doesn't exist
        """
        # Get the account
        account = crud.account.get(self.db, id=transaction_in.account_id)
        if not account:
            raise InvalidAccountError(f"Account {transaction_in.account_id} not found")

        # Validate category if provided
        if transaction_in.category_id:
            category = crud.category.get(self.db, id=transaction_in.category_id)
            if not category:
                raise InvalidAccountError(f"Category {transaction_in.category_id} not found")

        # Convert amount to Decimal for precision
        amount = Decimal(str(transaction_in.amount))

        try:
            # Create transaction record
            transaction_data = {
                "account_id": transaction_in.account_id,
                "amount": amount,
                "currency": account.currency,
                "category_id": transaction_in.category_id,
                "description": transaction_in.description,
                "transaction_date": transaction_in.transaction_date,
            }

            # Create the transaction (but don't commit yet)
            transaction = models.Transaction(**transaction_data)
            self.db.add(transaction)
            self.db.flush()  # Get the ID without committing

            # Update account balance
            account.balance = account.balance + amount  # type: ignore

            # Commit all changes atomically
            self.db.commit()
            self.db.refresh(transaction)

            return transaction

        except Exception as e:
            self.db.rollback()
            raise e

    def update_transaction(self, *, transaction_id: int, transaction_in: TransactionUpdate) -> models.Transaction:
        """Update a transaction with potential balance adjustments.

        Args:
            transaction_id: ID of the transaction to update
            transaction_in: Transaction update data

        Returns:
            Updated transaction object

        Raises:
            InvalidAccountError: If transaction doesn't exist
        """
        # Get the transaction
        transaction = crud.transaction.get(self.db, id=transaction_id)
        if not transaction:
            raise InvalidAccountError(f"Transaction {transaction_id} not found")

        # Get the account
        account = crud.account.get(self.db, id=transaction.account_id)
        if not account:
            raise InvalidAccountError(f"Account {transaction.account_id} not found")

        # If updating amount, handle balance recalculation
        update_data = transaction_in.model_dump(exclude_unset=True)
        if "amount" in update_data:
            return self._update_transaction_with_amount(transaction, transaction_in)
        else:
            # Simple update without amount change
            for field, value in update_data.items():
                setattr(transaction, field, value)

            self.db.commit()
            self.db.refresh(transaction)

            return transaction

    def _update_transaction_with_amount(
        self, transaction: models.Transaction, transaction_in: TransactionUpdate
    ) -> models.Transaction:
        """Update transaction with amount changes and balance adjustments."""
        # Get the account
        account = crud.account.get(self.db, id=transaction.account_id)
        if not account:
            raise InvalidAccountError(f"Account {transaction.account_id} not found")

        try:
            # First, reverse the current transaction's impact on balance
            account.balance = account.balance - transaction.amount  # type: ignore

            # Calculate new amount
            update_data = transaction_in.model_dump(exclude_unset=True)
            new_amount = Decimal(str(update_data["amount"]))

            # Apply new balance change
            account.balance = account.balance + new_amount  # type: ignore

            # Update transaction record
            update_data["amount"] = new_amount

            for field, value in update_data.items():
                setattr(transaction, field, value)

            # Commit all changes atomically
            self.db.commit()
            self.db.refresh(transaction)

            return transaction

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_transaction(self, *, transaction_id: int) -> models.Transaction:
        """Delete a transaction and reverse its balance impact.

        Args:
            transaction_id: ID of the transaction to delete

        Returns:
            Deleted transaction object

        Raises:
            InvalidAccountError: If transaction doesn't exist
        """
        # Get the transaction
        transaction = crud.transaction.get(self.db, id=transaction_id)
        if not transaction:
            raise InvalidAccountError(f"Transaction {transaction_id} not found")

        # Get the account
        account = crud.account.get(self.db, id=transaction.account_id)
        if not account:
            raise InvalidAccountError(f"Account {transaction.account_id} not found")

        try:
            # Reverse the transaction's impact on balance
            account.balance = account.balance - transaction.amount  # type: ignore

            # Delete the transaction
            self.db.delete(transaction)

            # Commit all changes atomically
            self.db.commit()

            return transaction

        except Exception as e:
            self.db.rollback()
            raise e