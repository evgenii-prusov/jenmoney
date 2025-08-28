from typing import Annotated
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from jenmoney import crud
from jenmoney.database import get_db
from jenmoney.exceptions import InvalidAccountError
from jenmoney.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
    TransactionListResponse,
)
from jenmoney.services.transaction_service import TransactionService

router = APIRouter()


@router.post("/", response_model=TransactionResponse)
def create_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_in: TransactionCreate,
) -> TransactionResponse:
    """Create a new transaction."""
    try:
        service = TransactionService(db)
        transaction = service.create_transaction(transaction_in=transaction_in)
        return TransactionResponse.model_validate(transaction)
    except InvalidAccountError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=TransactionListResponse)
def read_transactions(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    account_id: int | None = None,
    category_id: int | None = None,
) -> TransactionListResponse:
    """Retrieve transactions with optional filtering."""
    # Apply filters based on provided parameters
    if account_id is not None:
        transactions = crud.transaction.get_by_account_id(
            db, account_id=account_id, skip=skip, limit=limit
        )
        total = crud.transaction.count_by_account_id(db, account_id=account_id)
    elif category_id is not None:
        transactions = crud.transaction.get_by_category_id(
            db, category_id=category_id, skip=skip, limit=limit
        )
        total = crud.transaction.count_by_category_id(db, category_id=category_id)
    else:
        transactions = crud.transaction.get_multi(db, skip=skip, limit=limit)
        total = crud.transaction.count(db)

    return TransactionListResponse(
        items=[TransactionResponse.model_validate(t) for t in transactions],
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=ceil(total / limit) if total > 0 else 1,
    )


@router.get("/{transaction_id}", response_model=TransactionResponse)
def read_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """Get a specific transaction by ID."""
    transaction = crud.transaction.get(db, id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionResponse.model_validate(transaction)


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    *,
    db: Session = Depends(get_db),
    transaction_id: int,
    transaction_in: TransactionUpdate,
) -> TransactionResponse:
    """Update a transaction."""
    try:
        service = TransactionService(db)
        transaction = service.update_transaction(
            transaction_id=transaction_id, transaction_in=transaction_in
        )
        return TransactionResponse.model_validate(transaction)
    except InvalidAccountError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{transaction_id}", response_model=TransactionResponse)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
) -> TransactionResponse:
    """Delete a transaction."""
    try:
        service = TransactionService(db)
        transaction = service.delete_transaction(transaction_id=transaction_id)
        return TransactionResponse.model_validate(transaction)
    except InvalidAccountError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))