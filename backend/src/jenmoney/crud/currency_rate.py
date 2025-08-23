from jenmoney.crud.base import CRUDBase
from jenmoney.models.currency_rate import CurrencyRate
from jenmoney.schemas.currency_rate import CurrencyRateCreate, CurrencyRateUpdate


class CRUDCurrencyRate(CRUDBase[CurrencyRate, CurrencyRateCreate, CurrencyRateUpdate]):
    """CRUD operations for currency rates."""

    pass


currency_rate = CRUDCurrencyRate(CurrencyRate)
