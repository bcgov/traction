from fastapi import APIRouter

from .tenants import tenants_router

v1_innkeeper_router = APIRouter()

v1_innkeeper_router.include_router(tenants_router, prefix="/tenants", tags=["tenants"])
