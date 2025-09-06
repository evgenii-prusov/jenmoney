from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import Field

from jenmoney.schemas.base import BaseAPIModel
from jenmoney.schemas.category import CategoryResponse


class BudgetBase(BaseAPIModel):
    """Base budget model with core fields."""

    budget_year: Annotated[int, Field(ge=2000, le=2100)]
    budget_month: Annotated[int, Field(ge=1, le=12)]
    category_id: int
    planned_amount: Decimal
    currency: str = "USD"


class BudgetCreate(BaseAPIModel):
    """Model for creating a new budget entry."""

    budget_year: Annotated[int, Field(ge=2000, le=2100)]
    budget_month: Annotated[int, Field(ge=1, le=12)]
    category_id: int
    planned_amount: Decimal
    currency: str | None = None


class BudgetUpdate(BaseAPIModel):
    """Model for updating a budget entry. All fields are optional."""

    planned_amount: Decimal | None = None
    currency: str | None = None


class BudgetResponse(BudgetBase):
    """Model for budget responses. Includes all fields plus metadata."""

    id: int
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse | None = None
    actual_amount: Decimal = Decimal("0.00")  # Calculated field from transactions

    class Config:
        from_attributes = True


class BudgetSummary(BaseAPIModel):
    """Budget summary for a specific month showing totals."""

    budget_year: int
    budget_month: int
    total_planned: Decimal
    total_actual: Decimal
    currency: str
    categories_count: int
    # Separate income and expense totals for proper currency conversion display
    income_planned: Decimal = Decimal("0.00")
    income_actual: Decimal = Decimal("0.00")
    expense_planned: Decimal = Decimal("0.00")
    expense_actual: Decimal = Decimal("0.00")


class BudgetListResponse(BaseAPIModel):
    """Paginated response for budget listings."""

    items: list[BudgetResponse]
    total: int
    page: int = 1
    size: int = 10
    pages: int
    summary: BudgetSummary | None = None
