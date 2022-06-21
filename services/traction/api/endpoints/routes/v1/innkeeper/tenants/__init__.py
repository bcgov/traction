from fastapi import APIRouter

from .tenant import router as tenant
from .tenants import router as tenants

from .permissions import router as permissions

tenant.include_router(permissions, prefix="/{tenant_id}")

tenants_router = APIRouter()
tenants_router.include_router(tenants, tags=[])
tenants_router.include_router(tenant, tags=[])
