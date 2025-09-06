from sqlalchemy.orm import Session, joinedload

from jenmoney.models.category import Category, CategoryType
from jenmoney.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory:
    def create(self, db: Session, *, obj_in: CategoryCreate) -> Category:
        db_obj = Category(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Category | None:
        return (
            db.query(Category)
            .options(joinedload(Category.children))
            .filter(Category.id == id)
            .first()
        )

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        type_filter: CategoryType | None = None,
    ) -> list[Category]:
        query = db.query(Category).options(joinedload(Category.children))
        if type_filter:
            query = query.filter(Category.type == type_filter)
        return query.offset(skip).limit(limit).all()

    def get_root_categories(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        type_filter: CategoryType | None = None,
    ) -> list[Category]:
        """Get only root categories (categories with no parent) with their children."""
        query = (
            db.query(Category)
            .options(joinedload(Category.children))
            .filter(Category.parent_id.is_(None))
        )
        if type_filter:
            query = query.filter(Category.type == type_filter)
        return query.offset(skip).limit(limit).all()

    def count(self, db: Session, type_filter: CategoryType | None = None) -> int:
        query = db.query(Category)
        if type_filter:
            query = query.filter(Category.type == type_filter)
        return query.count()

    def count_root_categories(self, db: Session, type_filter: CategoryType | None = None) -> int:
        """Count only root categories (categories with no parent)."""
        query = db.query(Category).filter(Category.parent_id.is_(None))
        if type_filter:
            query = query.filter(Category.type == type_filter)
        return query.count()

    def update(self, db: Session, *, db_obj: Category, obj_in: CategoryUpdate) -> Category:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Category | None:
        obj = db.query(Category).filter(Category.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj

    def get_children(self, db: Session, parent_id: int) -> list[Category]:
        """Get all children of a specific category."""
        return db.query(Category).filter(Category.parent_id == parent_id).all()

    def get_all_descendant_ids(self, db: Session, category_id: int) -> list[int]:
        """Get all descendant category IDs including the category itself."""
        descendant_ids = [category_id]
        children = self.get_children(db, category_id)

        for child in children:
            # Use assert to help mypy understand the type
            assert child.id is not None
            descendant_ids.extend(self.get_all_descendant_ids(db, child.id))

        return descendant_ids


category = CRUDCategory()
