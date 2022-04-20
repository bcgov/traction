from fastapi import APIRouter

from .ledger import router as ledger

ledger_router = APIRouter()
ledger_router.include_router(ledger, tags=[])
