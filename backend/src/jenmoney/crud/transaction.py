from sqlalchemy.orm import Session

from jenmoney.crud.base import CRUDBase
from jenmoney.models.transaction import Transaction
from jenmoney.schemas.transaction import TransactionCreate, TransactionUpdate


class CRUDTransaction(CRUDBase[Transaction, TransactionCreate, TransactionUpdate]):
    def get_by_account_id(
        self, db: Session, *, account_id: int, skip: int = 0, limit: int = 100
    ) -> list[Transaction]:
        """Get transactions for a specific account."""
        return (
            db.query(self.model)
            .filter(self.model.account_id == account_id)
            .order_by(self.model.transaction_date.desc(), self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_category_id(
        self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> list[Transaction]:
        """Get transactions for a specific category."""
        return (
            db.query(self.model)
            .filter(self.model.category_id == category_id)
            .order_by(self.model.transaction_date.desc(), self.model.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count(self, db: Session) -> int:
        """Count total number of transactions."""
        return db.query(self.model).count()

    def count_by_account_id(self, db: Session, *, account_id: int) -> int:
        """Count transactions for a specific account."""
        return db.query(self.model).filter(self.model.account_id == account_id).count()

    def count_by_category_id(self, db: Session, *, category_id: int) -> int:
        """Count transactions for a specific category."""
        return db.query(self.model).filter(self.model.category_id == category_id).count()


transaction = CRUDTransaction(Transaction)