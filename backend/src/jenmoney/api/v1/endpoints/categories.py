from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from jenmoney import crud, schemas
from jenmoney.database import get_db

router = APIRouter()


@router.post("/", response_model=schemas.CategoryResponse)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: schemas.CategoryCreate,
) -> Any:
    """Create a new category."""
    category = crud.category.create(db=db, obj_in=category_in)
    return category


@router.get("/", response_model=schemas.CategoryListResponse)
def read_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
) -> Any:
    """Get list of categories with pagination."""
    categories = crud.category.get_multi(db, skip=skip, limit=limit)
    total = crud.category.count(db)
    
    return schemas.CategoryListResponse(
        items=categories,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=ceil(total / limit) if total > 0 else 1,
    )


@router.get("/{category_id}", response_model=schemas.CategoryResponse)
def read_category(*, db: Session = Depends(get_db), category_id: int) -> Any:
    """Get a specific category by ID."""
    category = crud.category.get(db=db, id=category_id)

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.patch("/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: schemas.CategoryUpdate,
) -> Any:
    """Update a category."""
    category = crud.category.get(db=db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = crud.category.update(db=db, db_obj=category, obj_in=category_in)
    return category


@router.delete("/{category_id}", response_model=schemas.CategoryResponse)
def delete_category(*, db: Session = Depends(get_db), category_id: int) -> Any:
    """Delete a category."""
    category = crud.category.delete(db=db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category