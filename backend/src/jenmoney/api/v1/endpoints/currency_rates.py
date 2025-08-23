from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from jenmoney import schemas
from jenmoney.crud.currency_rate import currency_rate
from jenmoney.database import get_db
from jenmoney.services.currency_service import CurrencyService

router = APIRouter()


@router.get("/", response_model=list[schemas.CurrencyRateResponse])
def list_currency_rates(
    db: Session = Depends(get_db),
) -> Any:
    """List all current exchange rates."""
    rates = currency_rate.get_multi(db, skip=0, limit=100)
    return rates


@router.post("/import/csv", response_model=dict)
async def import_rates_csv(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> Any:
    """Import currency rates from a CSV file."""
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    contents = await file.read()

    # Save to temporary file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as tmp:
        tmp.write(contents.decode("utf-8"))
        tmp_path = tmp.name

    try:
        service = CurrencyService(db)
        count = service.load_rates_from_csv(tmp_path)
        return {"message": f"Successfully imported {count} exchange rates"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing rates: {str(e)}")
    finally:
        import os

        os.unlink(tmp_path)


@router.post("/import/json", response_model=dict)
async def import_rates_json(
    *,
    db: Session = Depends(get_db),
    file: UploadFile = File(...),
) -> Any:
    """Import currency rates from a JSON file."""
    if not file.filename or not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be JSON")

    contents = await file.read()

    # Save to temporary file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp:
        tmp.write(contents.decode("utf-8"))
        tmp_path = tmp.name

    try:
        service = CurrencyService(db)
        count = service.load_rates_from_json(tmp_path)
        return {"message": f"Successfully imported {count} exchange rates"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing rates: {str(e)}")
    finally:
        import os

        os.unlink(tmp_path)


@router.get("/current", response_model=dict)
def get_current_rates(db: Session = Depends(get_db)) -> Any:
    """Get all current exchange rates to USD."""
    service = CurrencyService(db)
    rates = service.get_all_current_rates()
    return rates
