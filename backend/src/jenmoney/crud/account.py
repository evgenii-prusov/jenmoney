from sqlalchemy.orm import Session

from jenmoney.models.account import Account
from jenmoney.schemas.account import AccountCreate, AccountUpdate


class CRUDAccount:
    def create(self, db: Session, *, obj_in: AccountCreate) -> Account:
        db_obj = Account(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: int) -> Account | None:
        return db.query(Account).filter(Account.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Account]:
        return db.query(Account).offset(skip).limit(limit).all()

    def count(
        self,
        db: Session,
    ) -> int:
        return db.query(Account).count()

    def update(
        self,
        db: Session,
        *,
        db_obj: Account,
        obj_in: AccountUpdate,
    ) -> Account:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, id: int) -> Account | None:
        obj = db.query(Account).filter(Account.id == id).first()
        if obj:
            db.delete(obj)
            db.commit()
        return obj


account = CRUDAccount()
