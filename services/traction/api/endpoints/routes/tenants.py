import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from api.endpoints.dependencies.db import get_db
from api.services.tenants import create_new_tenant
from api.models.schema.tenants import (
    RequestCheckInSchema,
    ResponseCheckInSchema,
    OutTenantSchema,
)
from api.db.repositories.tenants import TenantsRepository

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/check-in",
    status_code=status.HTTP_201_CREATED,
    response_model=ResponseCheckInSchema,
)
async def tenant_check_in(
    payload: RequestCheckInSchema, db: AsyncSession = Depends(get_db)
) -> ResponseCheckInSchema:
    item = await create_new_tenant(payload=payload, db=db)
    return item


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[OutTenantSchema])
async def get_tenants(db: AsyncSession = Depends(get_db)) -> List[OutTenantSchema]:
    # this should take some query params, sorting and paging params...
    repo = TenantsRepository(db_session=db)
    items = await repo.find()
    return items


@router.get(
    "/{tenant_id}", status_code=status.HTTP_200_OK, response_model=OutTenantSchema
)
async def get_tenant(
    tenant_id: UUID, db: AsyncSession = Depends(get_db)
) -> OutTenantSchema:
    # this should take some query params, sorting and paging params...
    repo = TenantsRepository(db_session=db)
    item = await repo.get_by_id(tenant_id)
    return item
