from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from jenmoney import crud, schemas
from jenmoney.database import get_db
from jenmoney.models.category import CategoryType

router = APIRouter()


@router.post("/", response_model=schemas.CategoryResponse)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: schemas.CategoryCreate,
) -> Any:
    """Create a new category."""
    # Validate parent exists if parent_id is provided
    if category_in.parent_id is not None:
        parent = crud.category.get(db=db, id=category_in.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")
        # Prevent deep nesting - only allow 2 levels (parent -> child)
        if parent.parent_id is not None:
            raise HTTPException(
                status_code=400, detail="Cannot create more than 2 levels of categories"
            )
        # Ensure child category has the same type as parent
        if parent.type.value != category_in.type:
            raise HTTPException(
                status_code=400, detail="Child category must have the same type as parent"
            )

    category = crud.category.create(db=db, obj_in=category_in)
    return category


@router.get("/", response_model=schemas.CategoryListResponse)
def read_categories(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    hierarchical: bool = Query(
        False, description="Return only root categories with their children"
    ),
    type: CategoryType | None = Query(None, description="Filter by category type"),
) -> Any:
    """Get list of categories with pagination. Use hierarchical=true for tree view."""
    if hierarchical:
        categories = crud.category.get_root_categories(db, skip=skip, limit=limit, type_filter=type)
        total = crud.category.count_root_categories(db, type_filter=type)
    else:
        categories = crud.category.get_multi(db, skip=skip, limit=limit, type_filter=type)
        total = crud.category.count(db, type_filter=type)

    return schemas.CategoryListResponse(
        items=categories,
        total=total,
        page=(skip // limit) + 1,
        size=limit,
        pages=ceil(total / limit) if total > 0 else 1,
    )


@router.get("/hierarchy", response_model=list[schemas.CategoryResponse])
def read_categories_hierarchy(
    db: Session = Depends(get_db),
    type: CategoryType | None = Query(None, description="Filter by category type"),
) -> Any:
    """Get all categories in hierarchical structure (root categories with their children)."""
    categories = crud.category.get_root_categories(
        db, skip=0, limit=1000, type_filter=type
    )  # Get all root categories
    return categories


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

    # Validate parent_id if being updated
    if category_in.parent_id is not None:
        if category_in.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Category cannot be its own parent")

        parent = crud.category.get(db=db, id=category_in.parent_id)
        if not parent:
            raise HTTPException(status_code=400, detail="Parent category not found")

        # Prevent cycles - check if the parent is a child of this category
        if parent.parent_id == category_id:
            raise HTTPException(status_code=400, detail="Cannot set a child category as parent")

        # Prevent deep nesting - only allow 2 levels
        if parent.parent_id is not None:
            raise HTTPException(
                status_code=400, detail="Cannot create more than 2 levels of categories"
            )

        # Ensure type compatibility when changing parent
        category_type = category_in.type if category_in.type is not None else category.type.value
        if parent.type.value != category_type:
            raise HTTPException(
                status_code=400, detail="Child category must have the same type as parent"
            )

    # If changing type, validate all children have compatible type
    if category_in.type is not None and category_in.type != category.type.value:
        # Check if category has children and their types
        if category.children:
            for child in category.children:
                if child.type.value != category_in.type:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Cannot change type: child category '{child.name}' has different type",
                    )

    category = crud.category.update(db=db, db_obj=category, obj_in=category_in)
    return category


@router.delete("/{category_id}", response_model=schemas.CategoryResponse)
def delete_category(*, db: Session = Depends(get_db), category_id: int) -> Any:
    """Delete a category. If it has children, they will also be deleted."""
    category = crud.category.delete(db=db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category
