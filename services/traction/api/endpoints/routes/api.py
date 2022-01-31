from fastapi import APIRouter

from api.endpoints.routes import innkeeper, tenants

api_router = APIRouter()
api_router.include_router(innkeeper.router, prefix="/innkeeper", tags=["innkeeper"])
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
