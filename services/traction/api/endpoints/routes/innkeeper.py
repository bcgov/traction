import logging

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.services.innkeeper import hard_delete_tenant

from api.db.repositories.tenants import TenantsRepository


router = APIRouter()
logger = logging.getLogger(__name__)


@router.delete(
    "/tenants/{tenant_id}/hard-delete", status_code=status.HTTP_204_NO_CONTENT
)
async def tenant_hard_delete_tenant(
    tenant_id: UUID, db: AsyncSession = Depends(get_db)
):
    """HARD DELETE A TENANT, mostly for testing clean up"""
    # kick off the process of promoting this tenant to "issuer"
    tenant_repo = TenantsRepository(db_session=db)
    tenant = await tenant_repo.get_by_id(tenant_id)

    await hard_delete_tenant(tenant, db)

    return
