"""Transfer service for handling money transfers between accounts."""

from decimal import Decimal
from typing import Tuple

from sqlalchemy.orm import Session

from jenmoney import crud, models
from jenmoney.exceptions import (
    CurrencyConversionError,
    TransferValidationError,
    InsufficientFundsError,
    InvalidAccountError,
)
from jenmoney.schemas.transfer import TransferCreate, TransferUpdate
from jenmoney.services.currency_service import CurrencyService


class TransferService:
    """Service for handling transfers between accounts."""

    def __init__(self, db: Session):
        self.db = db
        self.currency_service = CurrencyService(db)

    def create_transfer(self, *, transfer_in: TransferCreate) -> models.Transfer:
        """Create a new transfer between accounts.

        Args:
            transfer_in: Transfer creation data

        Returns:
            Created transfer object

        Raises:
            InvalidAccountError: If accounts don't exist
            InsufficientFundsError: If source account has insufficient funds
            CurrencyConversionError: If currency conversion fails
        """
        # Validate accounts exist
        from_account = crud.account.get(self.db, id=transfer_in.from_account_id)
        to_account = crud.account.get(self.db, id=transfer_in.to_account_id)

        if not from_account:
            raise InvalidAccountError(f"Source account {transfer_in.from_account_id} not found")
        if not to_account:
            raise InvalidAccountError(f"Destination account {transfer_in.to_account_id} not found")

        # Calculate amounts and exchange rate
        from_amount = Decimal(str(transfer_in.from_amount))
        to_amount, exchange_rate = self._calculate_destination_amount(
            from_amount=from_amount,
            from_currency=str(from_account.currency),
            to_currency=str(to_account.currency),
            user_to_amount=Decimal(str(transfer_in.to_amount)) if transfer_in.to_amount else None,
        )

        # Validate sufficient funds
        if from_account.balance < from_amount:
            raise InsufficientFundsError(
                f"Insufficient funds in account {from_account.name}. "
                f"Available: {from_account.balance}, Required: {from_amount}"
            )

        # Start transaction
        try:
            # Create transfer record
            transfer_data = {
                "from_account_id": transfer_in.from_account_id,
                "to_account_id": transfer_in.to_account_id,
                "from_amount": from_amount,
                "from_currency": from_account.currency,
                "to_amount": to_amount,
                "to_currency": to_account.currency,
                "exchange_rate": exchange_rate,
                "description": transfer_in.description,
            }

            # Create the transfer (but don't commit yet)
            transfer = models.Transfer(**transfer_data)
            self.db.add(transfer)
            self.db.flush()  # Get the ID without committing

            # Update account balances
            from_account.balance = from_account.balance - from_amount  # type: ignore
            to_account.balance = to_account.balance + to_amount  # type: ignore

            # Commit all changes atomically
            self.db.commit()
            self.db.refresh(transfer)

            return transfer

        except Exception as e:
            self.db.rollback()
            raise e

    def delete_transfer(self, *, transfer_id: int) -> models.Transfer:
        """Delete a transfer and reverse account balance changes.

        Args:
            transfer_id: ID of the transfer to delete

        Returns:
            The deleted transfer object

        Raises:
            InvalidAccountError: If transfer or accounts don't exist
        """
        # Get the transfer
        transfer = crud.transfer.get(self.db, id=transfer_id)
        if not transfer:
            raise InvalidAccountError(f"Transfer {transfer_id} not found")

        # Get the accounts
        from_account = crud.account.get(self.db, id=transfer.from_account_id)
        to_account = crud.account.get(self.db, id=transfer.to_account_id)

        if not from_account:
            raise InvalidAccountError(f"Source account {transfer.from_account_id} not found")
        if not to_account:
            raise InvalidAccountError(f"Destination account {transfer.to_account_id} not found")

        try:
            # Reverse the account balance changes
            # Add back the from_amount to the from_account
            from_account.balance = from_account.balance + transfer.from_amount  # type: ignore
            # Subtract the to_amount from the to_account
            to_account.balance = to_account.balance - transfer.to_amount  # type: ignore

            # Delete the transfer
            self.db.delete(transfer)

            # Commit all changes atomically
            self.db.commit()

            return transfer

        except Exception as e:
            self.db.rollback()
            raise e

    def update_transfer(self, *, transfer_id: int, transfer_in: TransferUpdate) -> models.Transfer:
        """Update a transfer with potential balance adjustments.

        Args:
            transfer_id: ID of the transfer to update
            transfer_in: Transfer update data

        Returns:
            Updated transfer object

        Raises:
            InvalidAccountError: If transfer or accounts don't exist
            InsufficientFundsError: If account would have insufficient funds after update
        """
        # Get the transfer
        transfer = crud.transfer.get(self.db, id=transfer_id)
        if not transfer:
            raise InvalidAccountError(f"Transfer {transfer_id} not found")

        # If updating amounts, use the complex update method
        update_data = transfer_in.model_dump(exclude_unset=True)
        if "from_amount" in update_data or "to_amount" in update_data:
            # Amount update requires balance recalculation
            return self._update_transfer_with_amounts(transfer, transfer_in)
        else:
            # Simple description-only update
            return crud.transfer.update(self.db, db_obj=transfer, obj_in=transfer_in)

    def _update_transfer_with_amounts(
        self, transfer: models.Transfer, transfer_in: TransferUpdate
    ) -> models.Transfer:
        """Update transfer with amount changes and balance adjustments."""
        # Get the accounts
        from_account = crud.account.get(self.db, id=transfer.from_account_id)
        to_account = crud.account.get(self.db, id=transfer.to_account_id)

        if not from_account:
            raise InvalidAccountError(f"Source account {transfer.from_account_id} not found")
        if not to_account:
            raise InvalidAccountError(f"Destination account {transfer.to_account_id} not found")

        try:
            # First, reverse the current transfer's impact on balances
            from_account.balance = from_account.balance + transfer.from_amount  # type: ignore
            to_account.balance = to_account.balance - transfer.to_amount  # type: ignore

            # Calculate new amounts
            update_data = transfer_in.model_dump(exclude_unset=True)
            new_from_amount = (
                Decimal(str(update_data["from_amount"]))
                if "from_amount" in update_data
                else transfer.from_amount
            )
            user_to_amount = (
                Decimal(str(update_data["to_amount"])) if "to_amount" in update_data else None
            )

            new_to_amount, new_exchange_rate = self._calculate_destination_amount(
                from_amount=new_from_amount,
                from_currency=str(from_account.currency),
                to_currency=str(to_account.currency),
                user_to_amount=user_to_amount,
            )

            # Validate sufficient funds with new amount
            if from_account.balance < new_from_amount:
                raise InsufficientFundsError(
                    f"Insufficient funds in account {from_account.name}. "
                    f"Available: {from_account.balance}, Required: {new_from_amount}"
                )

            # Apply new balance changes
            from_account.balance = from_account.balance - new_from_amount  # type: ignore
            to_account.balance = to_account.balance + new_to_amount  # type: ignore

            # Update transfer record
            update_data["from_amount"] = new_from_amount
            update_data["to_amount"] = new_to_amount
            update_data["exchange_rate"] = new_exchange_rate

            for field, value in update_data.items():
                setattr(transfer, field, value)

            # Commit all changes atomically
            self.db.commit()
            self.db.refresh(transfer)

            return transfer

        except Exception as e:
            self.db.rollback()
            raise e

    def _calculate_destination_amount(
        self,
        from_amount: Decimal,
        from_currency: str,
        to_currency: str,
        user_to_amount: Decimal | None = None,
    ) -> Tuple[Decimal, Decimal | None]:
        """Calculate destination amount and exchange rate.

        Args:
            from_amount: Amount to transfer from source account
            from_currency: Source account currency
            to_currency: Destination account currency
            user_to_amount: Optional user-specified destination amount

        Returns:
            Tuple of (destination_amount, exchange_rate_used)
        """
        if from_currency == to_currency:
            # Same currency - no conversion needed
            if user_to_amount and user_to_amount != from_amount:
                raise TransferValidationError(
                    "For same-currency transfers, destination amount must equal source amount"
                )
            return from_amount, None

        # Different currencies - conversion needed
        if user_to_amount:
            # User specified destination amount - calculate exchange rate
            exchange_rate = user_to_amount / from_amount
            return user_to_amount, exchange_rate
        else:
            # Auto-calculate destination amount using current exchange rates
            try:
                exchange_rate_decimal = self.currency_service.get_current_rate(
                    from_currency, to_currency
                )
                to_amount = from_amount * exchange_rate_decimal
                return to_amount, exchange_rate_decimal
            except Exception as e:
                raise CurrencyConversionError(
                    f"Failed to convert {from_amount} {from_currency} to {to_currency}",
                    from_currency=from_currency,
                    to_currency=to_currency,
                    amount=str(from_amount),
                    original_error=e,
                )
