from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from jenmoney import crud, schemas, models
from jenmoney.database import get_db
from jenmoney.exceptions import (
    TransferValidationError,
    InsufficientFundsError,
    InvalidAccountError,
)
from jenmoney.services.transfer_service import TransferService

router = APIRouter()


def _convert_transfer_to_response(transfer: models.Transfer) -> schemas.TransferResponse:
    """Convert a Transfer model to TransferResponse schema."""
    return schemas.TransferResponse(
        id=transfer.id,  # type: ignore
        from_account_id=transfer.from_account_id,  # type: ignore
        to_account_id=transfer.to_account_id,  # type: ignore
        from_amount=float(transfer.from_amount),
        to_amount=float(transfer.to_amount),
        from_currency=transfer.from_currency,  # type: ignore
        to_currency=transfer.to_currency,  # type: ignore
        exchange_rate=float(transfer.exchange_rate) if transfer.exchange_rate else None,
        description=transfer.description,  # type: ignore
        created_at=transfer.created_at,  # type: ignore
        updated_at=transfer.updated_at,  # type: ignore
    )


@router.post("/", response_model=schemas.TransferResponse)
def create_transfer(
    *,
    db: Session = Depends(get_db),
    transfer_in: schemas.TransferCreate,
) -> Any:
    """Create a new transfer between accounts."""
    try:
        transfer_service = TransferService(db)
        transfer = transfer_service.create_transfer(transfer_in=transfer_in)

        # Convert to response format
        return _convert_transfer_to_response(transfer)

    except InvalidAccountError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientFundsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransferValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")


@router.get("/", response_model=schemas.TransferListResponse)
def read_transfers(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    account_id: int | None = Query(
        None, description="Filter by account ID (source or destination)"
    ),
) -> Any:
    """List transfers with optional filtering by account."""
    if account_id:
        transfers = crud.transfer.get_by_account_id(
            db, account_id=account_id, skip=skip, limit=limit
        )
        total = crud.transfer.count_by_account_id(db, account_id=account_id)
    else:
        transfers = crud.transfer.get_multi(db, skip=skip, limit=limit)
        total = crud.transfer.count(db)

    # Convert to response format
    transfer_responses = [_convert_transfer_to_response(transfer) for transfer in transfers]

    return {
        "items": transfer_responses,
        "total": total,
        "page": skip // limit + 1,
        "size": limit,
        "pages": (total + limit - 1) // limit,
    }


@router.get("/{transfer_id}", response_model=schemas.TransferResponse)
def read_transfer(
    *,
    db: Session = Depends(get_db),
    transfer_id: int,
) -> Any:
    """Get a specific transfer by ID."""
    transfer = crud.transfer.get(db=db, id=transfer_id)
    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    return _convert_transfer_to_response(transfer)


@router.patch("/{transfer_id}", response_model=schemas.TransferResponse)
def update_transfer(
    *,
    db: Session = Depends(get_db),
    transfer_id: int,
    transfer_in: schemas.TransferUpdate,
) -> Any:
    """Update a transfer (description and/or amounts)."""
    try:
        transfer_service = TransferService(db)
        transfer = transfer_service.update_transfer(
            transfer_id=transfer_id, transfer_in=transfer_in
        )
        return _convert_transfer_to_response(transfer)

    except InvalidAccountError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InsufficientFundsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except TransferValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer update failed: {str(e)}")


@router.delete("/{transfer_id}", response_model=schemas.TransferResponse)
def delete_transfer(
    *,
    db: Session = Depends(get_db),
    transfer_id: int,
) -> Any:
    """Delete a transfer by ID and reverse account balance changes."""
    try:
        transfer_service = TransferService(db)
        transfer = transfer_service.delete_transfer(transfer_id=transfer_id)
        return _convert_transfer_to_response(transfer)

    except InvalidAccountError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transfer deletion failed: {str(e)}")
