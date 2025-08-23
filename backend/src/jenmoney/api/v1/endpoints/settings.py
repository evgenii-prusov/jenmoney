from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from jenmoney import schemas
from jenmoney.crud.user_settings import user_settings
from jenmoney.database import get_db

router = APIRouter()


@router.get("/", response_model=schemas.UserSettingsResponse)
def get_settings(db: Session = Depends(get_db)) -> Any:
    """Get user settings."""
    settings = user_settings.get_or_create(db)
    return settings


@router.patch("/", response_model=schemas.UserSettingsResponse)
def update_settings(
    *,
    db: Session = Depends(get_db),
    settings_in: schemas.UserSettingsUpdate,
) -> Any:
    """Update user settings."""
    settings = user_settings.get_or_create(db)
    settings = user_settings.update(db=db, db_obj=settings, obj_in=settings_in)
    return settings
