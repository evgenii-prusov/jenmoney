from sqlalchemy.orm import Session

from jenmoney.models.category import Category
from jenmoney.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory:
    def create(self, db: Session, *, obj_in: CategoryCreate) -> Category:
        db_obj = Category(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Category | None:
        return db.query(Category).filter(Category.id == id).first()

    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> list[Category]:
        return db.query(Category).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(Category).count()

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


category = CRUDCategory()