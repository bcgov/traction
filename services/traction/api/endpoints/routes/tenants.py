import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.db.models.tenant import TenantRead
from api.endpoints.dependencies.db import get_db
from api.db.repositories.tenants import TenantsRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{tenant_id}", status_code=status.HTTP_200_OK, response_model=TenantRead)
async def get_tenant(tenant_id: UUID, db: AsyncSession = Depends(get_db)) -> TenantRead:
    # this should take some query params, sorting and paging params...
    repo = TenantsRepository(db_session=db)
    item = await repo.get_by_id(tenant_id)
    return item
