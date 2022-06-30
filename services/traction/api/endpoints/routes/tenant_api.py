from fastapi import APIRouter

from api.endpoints.routes import credentials

tenant_router = APIRouter()
tenant_router.include_router(credentials.router, prefix="/credentials", tags=[])
