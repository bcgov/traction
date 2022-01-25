from fastapi import APIRouter

from api.endpoints.routes import tenants

api_router = APIRouter()
api_router.include_router(tenants.router, prefix="/tenants", tags=["tenants"])
