import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.db.errors import DoesNotExist
from api.db.models.tenant import TenantRead
from api.db.models.tenant_issuer import TenantIssuerRead, TenantIssuerCreate
from api.endpoints.dependencies.db import get_db
from api.services.innkeeper import create_new_tenant
from api.endpoints.models.innkeeper import (
    CheckInRequest,
    CheckInResponse,
)
from api.db.repositories.tenants import TenantsRepository
from api.db.repositories.tenant_issuers import TenantIssuersRepository


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/check-in",
    status_code=status.HTTP_201_CREATED,
    response_model=CheckInResponse,
)
async def check_in_tenant(
    payload: CheckInRequest, db: AsyncSession = Depends(get_db)
) -> CheckInResponse:
    item = await create_new_tenant(payload=payload, db=db)
    return item


@router.get("/tenants", status_code=status.HTTP_200_OK, response_model=List[TenantRead])
async def get_tenants(db: AsyncSession = Depends(get_db)) -> List[TenantRead]:
    # this should take some query params, sorting and paging params...
    repo = TenantsRepository(db_session=db)
    items = await repo.find()
    return items


@router.get(
    "/tenants/{tenant_id}", status_code=status.HTTP_200_OK, response_model=TenantRead
)
async def get_tenant(tenant_id: UUID, db: AsyncSession = Depends(get_db)) -> TenantRead:
    # this should take some query params, sorting and paging params...
    repo = TenantsRepository(db_session=db)
    item = await repo.get_by_id(tenant_id)
    return item


@router.get(
    "/issuers",
    status_code=status.HTTP_200_OK,
    response_model=List[TenantIssuerRead],
)
async def get_tenant_issuers(
    db: AsyncSession = Depends(get_db),
) -> List[TenantIssuerRead]:
    # return status of tenant "issuers"
    issuer_repo = TenantIssuersRepository(db_session=db)
    tenant_issuers = await issuer_repo.find()
    return tenant_issuers


@router.get(
    "/issuers/{tenant_id}",
    status_code=status.HTTP_200_OK,
    response_model=TenantIssuerRead,
)
async def get_tenant_issuer(
    tenant_id: UUID, db: AsyncSession = Depends(get_db)
) -> TenantIssuerRead:
    # TODO return status of tenant "issuer"
    issuer_repo = TenantIssuersRepository(db_session=db)
    tenant_issuer = await issuer_repo.get_by_tenant_id(tenant_id)
    return tenant_issuer


@router.post(
    "/issuers/{tenant_id}",
    status_code=status.HTTP_200_OK,
    response_model=TenantIssuerRead,
)
async def make_tenant_issuer(
    tenant_id: UUID, db: AsyncSession = Depends(get_db)
) -> TenantIssuerRead:
    # kick off the process of promoting this tenant to "issuer"
    tenant_repo = TenantsRepository(db_session=db)
    tenant = await tenant_repo.get_by_id(tenant_id)
    try:
        issuer_repo = TenantIssuersRepository(db_session=db)
        tenant_issuer = await issuer_repo.get_by_wallet_id(tenant.wallet_id)
    except DoesNotExist:
        new_issuer = TenantIssuerCreate(
            tenant_id=tenant.id,
            wallet_id=tenant.wallet_id,
        )
        tenant_issuer = await issuer_repo.create(new_issuer)
    return tenant_issuer
