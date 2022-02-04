from fastapi import APIRouter

from api.endpoints.routes import connections, ledger, tenant_admin

tenant_router = APIRouter()
tenant_router.include_router(
    connections.router, prefix="/connections", tags=["connections"]
)
tenant_router.include_router(ledger.router, prefix="/ledger", tags=["ledger"])
tenant_router.include_router(tenant_admin.router, prefix="/admin", tags=["admin"])
