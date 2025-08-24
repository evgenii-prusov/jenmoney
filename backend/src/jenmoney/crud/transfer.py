from sqlalchemy.orm import Session

from jenmoney.crud.base import CRUDBase
from jenmoney.models.transfer import Transfer
from jenmoney.schemas.transfer import TransferCreate, TransferUpdate


class CRUDTransfer(CRUDBase[Transfer, TransferCreate, TransferUpdate]):
    def get_by_account_id(
        self, db: Session, *, account_id: int, skip: int = 0, limit: int = 100
    ) -> list[Transfer]:
        """Get transfers involving a specific account (either as source or destination)."""
        return (
            db.query(self.model)
            .filter(
                (self.model.from_account_id == account_id)
                | (self.model.to_account_id == account_id)
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_between_accounts(
        self,
        db: Session,
        *,
        from_account_id: int,
        to_account_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Transfer]:
        """Get transfers between two specific accounts."""
        return (
            db.query(self.model)
            .filter(
                self.model.from_account_id == from_account_id,
                self.model.to_account_id == to_account_id,
            )
            .order_by(self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self, db: Session) -> int:
        """Count total number of transfers."""
        return db.query(self.model).count()

    def count_by_account_id(self, db: Session, *, account_id: int) -> int:
        """Count transfers involving a specific account."""
        return (
            db.query(self.model)
            .filter(
                (self.model.from_account_id == account_id)
                | (self.model.to_account_id == account_id)
            )
            .count()
        )


transfer = CRUDTransfer(Transfer)
