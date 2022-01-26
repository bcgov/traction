from fastapi import APIRouter

from api.endpoints.routes import innkeeper, tenants, connections, ledger

api_router = APIRouter()
api_router.include_router(connections.router, prefix="/connections", tags=["connections"])
api_router.include_router(ledger.router, prefix="/ledger", tags=["ledger"])
api_router.include_router(innkeeper.router, prefix="/innkeeper", tags=["innkeeper"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
