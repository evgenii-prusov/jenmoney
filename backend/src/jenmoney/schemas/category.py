from datetime import datetime
from typing import Annotated, Optional, List, TYPE_CHECKING

from pydantic import Field

from jenmoney.schemas.base import BaseAPIModel

if TYPE_CHECKING:
    from typing import ForwardRef
    CategoryResponseRef = ForwardRef('CategoryResponse')
else:
    CategoryResponseRef = 'CategoryResponse'


class CategoryBase(BaseAPIModel):
    """Base category model with core fields that are always present."""

    name: Annotated[str, Field(min_length=1, max_length=100)]


class CategoryCreate(CategoryBase):
    """Model for creating a new category. All fields from base are required."""

    description: str | None = None
    parent_id: int | None = None


class CategoryUpdate(BaseAPIModel):
    """Model for updating a category. All fields are optional."""

    name: Annotated[str, Field(min_length=1, max_length=100)] | None = None
    description: str | None = None
    parent_id: int | None = None


class CategoryResponse(CategoryBase):
    """Model for category responses. Includes all fields plus metadata."""

    id: int
    description: str | None = None
    parent_id: int | None = None
    created_at: datetime
    updated_at: datetime
    children: List[CategoryResponseRef] = []

    class Config:
        from_attributes = True


# Update the forward reference
CategoryResponse.model_rebuild()


class CategoryInDB(CategoryResponse):
    """Internal model with all database fields."""

    pass


class CategoryListResponse(BaseAPIModel):
    """Paginated response for category listings."""

    items: list[CategoryResponse]
    total: int
    page: int = 1
    size: int = 10
    pages: int