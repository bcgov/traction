from fastapi import APIRouter

from .contacts import contacts_router
from .ledger import ledger_router
from .issuer import issuer_router

v1_tenant_router = APIRouter()
v1_tenant_router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
v1_tenant_router.include_router(ledger_router, prefix="/ledger", tags=["ledger"])
v1_tenant_router.include_router(issuer_router, prefix="/issuer", tags=["issuer"])
