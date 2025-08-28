from fastapi import APIRouter

from jenmoney.api.v1.endpoints import accounts, categories, currency_rates, settings, transactions, transfers

api_router = APIRouter()
api_router.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(currency_rates.router, prefix="/currency-rates", tags=["currency-rates"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
api_router.include_router(transfers.router, prefix="/transfers", tags=["transfers"])
