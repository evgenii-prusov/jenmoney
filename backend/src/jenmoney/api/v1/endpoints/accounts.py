from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from jenmoney import crud, schemas
from jenmoney.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.AccountResponse)
def create_account(
    *,
    db: Session = Depends(get_db),
    account_in: schemas.AccountCreate,
) -> Any:
    account = crud.account.create(db=db, obj_in=account_in)
    return account


@router.get("/", response_model=schemas.AccountListResponse)
def read_accounts(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    accounts = crud.account.get_multi(db, skip=skip, limit=limit)
    total = crud.account.count(db)

    return {
        "items": accounts,
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
    return account


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
    return account


@router.delete("/{account_id}", response_model=schemas.AccountResponse)
def delete_account(*, db: Session = Depends(get_db), account_id: int) -> Any:
    account = crud.account.get(db=db, id=account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account = crud.account.delete(db=db, id=account_id)
    return account
