from math import ceil
from typing import Any
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from jenmoney import crud, schemas
from jenmoney.crud.user_settings import user_settings
from jenmoney.database import get_db
from jenmoney.services.currency_service import CurrencyService

router = APIRouter()


@router.post("/", response_model=schemas.BudgetResponse)
def create_budget(
    *,
    db: Session = Depends(get_db),
    budget_in: schemas.BudgetCreate,
) -> Any:
    """Create a new budget entry."""
    try:
        budget_obj = crud.budget.create_with_validation(db, obj_in=budget_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Calculate actual spending for this category/period
    actual_amount = crud.budget.get_actual_spending(
        db,
        category_id=budget_obj.category_id,
        year=budget_obj.budget_year,
        month=budget_obj.budget_month,
    )

    # Add actual amount to response
    response_data = schemas.BudgetResponse.model_validate(budget_obj)
    response_data.actual_amount = actual_amount

    return response_data


@router.get("/", response_model=schemas.BudgetListResponse)
def read_budgets(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    year: int = Query(..., ge=2000, le=2100, description="Budget year"),
    month: int = Query(..., ge=1, le=12, description="Budget month"),
) -> Any:
    """Get budgets for a specific month with actual spending data."""
    budgets = crud.budget.get_by_period(db, year=year, month=month, skip=skip, limit=limit)
    total = crud.budget.count_by_period(db, year=year, month=month)

    # Get user settings for default currency
    settings = user_settings.get_or_create(db)
    currency_service = CurrencyService(db)

    # Get actual spending for all categories in this period
    actual_spending = crud.budget.get_actual_spending_all_categories(db, year=year, month=month)

    # Build response with actual amounts
    budget_responses = []
    total_planned = Decimal("0.00")
    total_actual = Decimal("0.00")

    for budget_obj in budgets:
        actual_amount = actual_spending.get(budget_obj.category_id, Decimal("0.00"))
        response_data = schemas.BudgetResponse.model_validate(budget_obj)
        response_data.actual_amount = actual_amount
        budget_responses.append(response_data)

        # Convert amounts to default currency for summary totals
        try:
            planned_in_default = currency_service.convert_amount(
                Decimal(str(budget_obj.planned_amount)),
                str(budget_obj.currency),
                str(settings.default_currency),
            )
            actual_in_default = currency_service.convert_amount(
                actual_amount,
                str(budget_obj.currency),
                str(settings.default_currency),
            )
            total_planned += planned_in_default
            total_actual += actual_in_default
        except Exception:
            # If conversion fails, use original amounts as fallback
            total_planned += Decimal(str(budget_obj.planned_amount))
            total_actual += actual_amount

    # Create summary with default currency
    summary = schemas.BudgetSummary(
        budget_year=year,
        budget_month=month,
        total_planned=total_planned,
        total_actual=total_actual,
        currency=str(settings.default_currency),
        categories_count=len(budgets),
    )

    return schemas.BudgetListResponse(
        items=budget_responses,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=ceil(total / limit) if limit > 0 else 1,
        summary=summary,
    )


@router.get("/{budget_id}", response_model=schemas.BudgetResponse)
def read_budget(*, db: Session = Depends(get_db), budget_id: int) -> Any:
    """Get a specific budget by ID."""
    budget_obj = crud.budget.get(db, id=budget_id)
    if budget_obj is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Calculate actual spending
    actual_amount = crud.budget.get_actual_spending(
        db,
        category_id=budget_obj.category_id,
        year=budget_obj.budget_year,
        month=budget_obj.budget_month,
    )

    response_data = schemas.BudgetResponse.model_validate(budget_obj)
    response_data.actual_amount = actual_amount

    return response_data


@router.patch("/{budget_id}", response_model=schemas.BudgetResponse)
def update_budget(
    *,
    db: Session = Depends(get_db),
    budget_id: int,
    budget_in: schemas.BudgetUpdate,
) -> Any:
    """Update a budget entry."""
    budget_obj = crud.budget.get(db, id=budget_id)
    if budget_obj is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    budget_obj = crud.budget.update(db, db_obj=budget_obj, obj_in=budget_in)

    # Calculate actual spending
    actual_amount = crud.budget.get_actual_spending(
        db,
        category_id=budget_obj.category_id,
        year=budget_obj.budget_year,
        month=budget_obj.budget_month,
    )

    response_data = schemas.BudgetResponse.model_validate(budget_obj)
    response_data.actual_amount = actual_amount

    return response_data


@router.delete("/{budget_id}", response_model=schemas.BudgetResponse)
def delete_budget(*, db: Session = Depends(get_db), budget_id: int) -> Any:
    """Delete a budget entry."""
    budget_obj = crud.budget.get(db, id=budget_id)
    if budget_obj is None:
        raise HTTPException(status_code=404, detail="Budget not found")

    # Calculate actual spending before deletion
    actual_amount = crud.budget.get_actual_spending(
        db,
        category_id=budget_obj.category_id,
        year=budget_obj.budget_year,
        month=budget_obj.budget_month,
    )

    response_data = schemas.BudgetResponse.model_validate(budget_obj)
    response_data.actual_amount = actual_amount

    crud.budget.remove(db, id=budget_id)

    return response_data
