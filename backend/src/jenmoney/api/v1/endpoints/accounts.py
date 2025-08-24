from decimal import Decimal
from typing import Any
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from jenmoney import crud, schemas
from jenmoney.crud.user_settings import user_settings
from jenmoney.database import get_db
from jenmoney.services.currency_service import CurrencyService
from jenmoney.services.account_enrichment_service import AccountEnrichmentService

router = APIRouter()


@router.post("/", response_model=schemas.AccountResponse)
def create_account(
    *,
    db: Session = Depends(get_db),
    account_in: schemas.AccountCreate,
) -> Any:
    account = crud.account.create(db=db, obj_in=account_in)
    enrichment_service = AccountEnrichmentService(db)
    return enrichment_service.enrich_account_full(account)


@router.get("/", response_model=schemas.AccountListResponse)
def read_accounts(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    accounts = crud.account.get_multi(db, skip=skip, limit=limit)
    total = crud.account.count(db)

    enrichment_service = AccountEnrichmentService(db)
    enriched_accounts = [
        enrichment_service.enrich_account_full(account) for account in accounts
    ]

    return {
        "items": enriched_accounts,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{account_id}", response_model=schemas.AccountResponse)
def read_account(*, db: Session = Depends(get_db), account_id: int) -> Any:
    account = crud.account.get(db=db, id=account_id)

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    enrichment_service = AccountEnrichmentService(db)
    return enrichment_service.enrich_account_full(account)


@router.patch("/{account_id}", response_model=schemas.AccountResponse)
def update_account(
    *,
    db: Session = Depends(get_db),
    account_id: int,
    account_in: schemas.AccountUpdate,
) -> Any:
    account = crud.account.get(db=db, id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account = crud.account.update(db=db, db_obj=account, obj_in=account_in)

    enrichment_service = AccountEnrichmentService(db)
    return enrichment_service.enrich_account_full(account)


@router.delete("/{account_id}", response_model=schemas.AccountResponse)
def delete_account(*, db: Session = Depends(get_db), account_id: int) -> Any:
    account = crud.account.get(db=db, id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Calculate percentage before deletion
    enrichment_service = AccountEnrichmentService(db)
    percentage = enrichment_service.get_account_percentage(account_id)

    deleted_account = crud.account.delete(db=db, id=account_id)

    # Since we verified the account exists before deletion, it should never be None
    if not deleted_account:
        raise HTTPException(status_code=500, detail="Failed to delete account")

    enriched_account = enrichment_service.enrich_account_with_conversion(deleted_account)
    enriched_account["percentage_of_total"] = percentage

    return enriched_account


@router.get("/total-balance/", response_model=schemas.TotalBalanceResponse)
def get_total_balance(db: Session = Depends(get_db)) -> Any:
    """Calculate total balance across all accounts in the default currency."""
    accounts = crud.account.get_multi(db, skip=0, limit=10000)
    settings = user_settings.get_or_create(db)
    currency_service = CurrencyService(db)

    total_balance = Decimal("0")
    currency_totals = {}

    for account in accounts:
        # Add to currency totals
        if account.currency not in currency_totals:
            currency_totals[account.currency] = Decimal("0")
        currency_totals[account.currency] += Decimal(str(account.balance))

        # Convert to default currency and add to total
        if account.currency == settings.default_currency:
            total_balance += Decimal(str(account.balance))
        else:
            try:
                converted = currency_service.convert_amount(
                    Decimal(str(account.balance)),
                    str(account.currency),
                    str(settings.default_currency),
                )
                total_balance += converted
            except Exception:
                # If conversion fails, skip this account
                pass

    return {
        "total_balance": float(total_balance),
        "default_currency": settings.default_currency,
        "currency_breakdown": {cur: float(amt) for cur, amt in currency_totals.items()},
    }
