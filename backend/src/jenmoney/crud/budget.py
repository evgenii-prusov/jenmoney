from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, extract

from jenmoney.crud.base import CRUDBase
from jenmoney.models.budget import Budget
from jenmoney.models.transaction import Transaction
from jenmoney.models.category import Category, CategoryType
from jenmoney.schemas.budget import BudgetCreate, BudgetUpdate


class CRUDBudget(CRUDBase[Budget, BudgetCreate, BudgetUpdate]):
    def get_by_period(
        self, db: Session, *, year: int, month: int, skip: int = 0, limit: int = 100
    ) -> list[Budget]:
        """Get budgets for a specific year and month."""
        return (
            db.query(self.model)
            .options(joinedload(Budget.category))
            .filter(and_(Budget.budget_year == year, Budget.budget_month == month))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_period(self, db: Session, *, year: int, month: int) -> int:
        """Count budgets for a specific year and month."""
        return (
            db.query(self.model)
            .filter(and_(Budget.budget_year == year, Budget.budget_month == month))
            .count()
        )

    def get_by_category_and_period(
        self, db: Session, *, category_id: int, year: int, month: int
    ) -> Budget | None:
        """Get budget for a specific category in a specific month."""
        return (
            db.query(self.model)
            .filter(
                and_(
                    Budget.category_id == category_id,
                    Budget.budget_year == year,
                    Budget.budget_month == month,
                )
            )
            .first()
        )

    def get_actual_spending(
        self, db: Session, *, category_id: int, year: int, month: int
    ) -> Decimal:
        """Calculate actual spending for a category in a specific month."""
        result = (
            db.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(
                and_(
                    Transaction.category_id == category_id,
                    extract("year", Transaction.transaction_date) == year,
                    extract("month", Transaction.transaction_date) == month,
                    Transaction.amount < 0,  # Only expenses (negative amounts)
                )
            )
            .scalar()
        )
        # Return absolute value since expenses are negative
        return abs(Decimal(str(result or 0)))

    def get_actual_spending_all_categories(
        self, db: Session, *, year: int, month: int
    ) -> dict[int, Decimal]:
        """Get actual spending for all categories in a specific month."""
        results = (
            db.query(
                Transaction.category_id,
                func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            )
            .filter(
                and_(
                    Transaction.category_id.isnot(None),
                    extract("year", Transaction.transaction_date) == year,
                    extract("month", Transaction.transaction_date) == month,
                    Transaction.amount < 0,  # Only expenses
                )
            )
            .group_by(Transaction.category_id)
            .all()
        )

        # Return dict with category_id -> absolute spending amount
        return {category_id: abs(Decimal(str(total))) for category_id, total in results}

    def create_with_validation(self, db: Session, *, obj_in: BudgetCreate) -> Budget:
        """Create budget with validation that category is expense type."""
        # Check if category exists and is expense type
        category = db.query(Category).filter(Category.id == obj_in.category_id).first()
        if not category:
            raise ValueError(f"Category with id {obj_in.category_id} not found")

        if category.type != CategoryType.expense:
            raise ValueError("Budget can only be created for expense categories")

        # Check if budget already exists for this category and period
        existing = self.get_by_category_and_period(
            db, category_id=obj_in.category_id, year=obj_in.budget_year, month=obj_in.budget_month
        )
        if existing:
            raise ValueError(
                f"Budget already exists for category {obj_in.category_id} "
                f"in {obj_in.budget_month}/{obj_in.budget_year}"
            )

        return self.create(db, obj_in=obj_in)


budget = CRUDBudget(Budget)
