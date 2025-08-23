from sqlalchemy.orm import Session

from jenmoney.crud.base import CRUDBase
from jenmoney.models.user_settings import UserSettings
from jenmoney.schemas.user_settings import UserSettingsCreate, UserSettingsUpdate


class CRUDUserSettings(CRUDBase[UserSettings, UserSettingsCreate, UserSettingsUpdate]):
    """CRUD operations for user settings."""

    def get_or_create(self, db: Session) -> UserSettings:
        """Get the user settings or create default ones if they don't exist.

        For now, we use a single settings record (id=1) since we don't have auth yet.
        """
        settings = db.query(self.model).filter(self.model.id == 1).first()
        if not settings:
            settings = self.model(id=1, default_currency="USD")
            db.add(settings)
            db.commit()
            db.refresh(settings)
        return settings


user_settings = CRUDUserSettings(UserSettings)
