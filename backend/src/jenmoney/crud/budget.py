from decimal import Decimal
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, extract

from jenmoney.crud.base import CRUDBase
from jenmoney.models.budget import Budget
from jenmoney.models.transaction import Transaction
from jenmoney.models.account import Account
from jenmoney.models.category import Category, CategoryType
from jenmoney.schemas.budget import BudgetCreate, BudgetUpdate
from jenmoney.services.currency_service import CurrencyService


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

    def get_actual_amount(
        self, db: Session, *, category_id: int, year: int, month: int
    ) -> Decimal:
        """Calculate actual amount for a category and all its children in a specific month.
        
        For expense categories, sums negative transaction amounts (expenses).
        For income categories, sums positive transaction amounts (income).
        """
        # Import here to avoid circular imports
        from jenmoney.crud.category import category as category_crud

        # Get the budget to know its currency
        budget = self.get_by_category_and_period(
            db, category_id=category_id, year=year, month=month
        )
        if not budget:
            return Decimal("0.00")

        # Get the category to determine its type
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return Decimal("0.00")

        budget_currency = str(budget.currency)
        currency_service = CurrencyService(db)

        # Get all descendant category IDs (including the category itself)
        descendant_ids = category_crud.get_all_descendant_ids(db, category_id)

        # Determine transaction filter based on category type
        if category.type == CategoryType.expense:
            # For expenses, get negative amounts (money going out)
            amount_filter = Transaction.amount < 0
        else:  # CategoryType.income
            # For income, get positive amounts (money coming in)
            amount_filter = Transaction.amount > 0

        # Get all transactions for these categories in the specified period
        transactions = (
            db.query(Transaction, Account.currency)
            .join(Account, Transaction.account_id == Account.id)
            .filter(
                and_(
                    Transaction.category_id.in_(descendant_ids),
                    extract("year", Transaction.transaction_date) == year,
                    extract("month", Transaction.transaction_date) == month,
                    amount_filter,
                )
            )
            .all()
        )

        total_amount = Decimal("0.00")
        for transaction, transaction_currency in transactions:
            # Convert transaction amount to budget currency
            transaction_amount = abs(Decimal(str(transaction.amount)))
            try:
                converted_amount = currency_service.convert_amount(
                    transaction_amount, str(transaction_currency), budget_currency
                )
                total_amount += converted_amount
            except Exception:
                # If conversion fails, use original amount as fallback
                total_amount += transaction_amount

        return total_amount

    def get_actual_amounts_all_categories(
        self, db: Session, *, year: int, month: int
    ) -> dict[int, Decimal]:
        """Get actual amounts for all categories in a specific month.

        For each category, includes amounts from the category itself and all its children.
        For expense categories, sums expenses. For income categories, sums income.
        Amounts are converted to each budget's currency.
        """
        # Import here to avoid circular imports
        from jenmoney.crud.category import category as category_crud

        # Get all budgets for this period to know which categories we need to calculate
        budgets = self.get_by_period(db, year=year, month=month)
        currency_service = CurrencyService(db)

        amounts_dict: dict[int, Decimal] = {}
        for budget in budgets:
            # Get the category to determine its type
            category = db.query(Category).filter(Category.id == budget.category_id).first()
            if not category:
                amounts_dict[budget.category_id] = Decimal("0.00")
                continue

            # Get all descendant category IDs (including the category itself)
            assert budget.category_id is not None
            descendant_ids = category_crud.get_all_descendant_ids(db, budget.category_id)

            # Determine transaction filter based on category type
            if category.type == CategoryType.expense:
                # For expenses, get negative amounts (money going out)
                amount_filter = Transaction.amount < 0
            else:  # CategoryType.income
                # For income, get positive amounts (money coming in)
                amount_filter = Transaction.amount > 0

            # Get all transactions for these categories in the specified period
            transactions = (
                db.query(Transaction, Account.currency)
                .join(Account, Transaction.account_id == Account.id)
                .filter(
                    and_(
                        Transaction.category_id.in_(descendant_ids),
                        extract("year", Transaction.transaction_date) == year,
                        extract("month", Transaction.transaction_date) == month,
                        amount_filter,
                    )
                )
                .all()
            )

            budget_currency = str(budget.currency)
            total_amount = Decimal("0.00")

            for transaction, transaction_currency in transactions:
                # Convert transaction amount to budget currency
                transaction_amount = abs(Decimal(str(transaction.amount)))
                try:
                    converted_amount = currency_service.convert_amount(
                        transaction_amount, str(transaction_currency), budget_currency
                    )
                    total_amount += converted_amount
                except Exception:
                    # If conversion fails, use original amount as fallback
                    total_amount += transaction_amount

            assert budget.category_id is not None
            amounts_dict[budget.category_id] = total_amount

        return amounts_dict

    def create_with_validation(self, db: Session, *, obj_in: BudgetCreate) -> Budget:
        """Create budget with validation."""
        # Check if category exists
        category = db.query(Category).filter(Category.id == obj_in.category_id).first()
        if not category:
            raise ValueError(f"Category with id {obj_in.category_id} not found")

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
