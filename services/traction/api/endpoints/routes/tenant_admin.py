import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette_context import context

from api.db.models.tenant import TenantRead
from api.db.models.tenant_webhook import TenantWebhookRead
from api.endpoints.dependencies.db import get_db
from api.db.repositories.tenants import TenantsRepository
from api.db.repositories.tenant_webhooks import TenantWebhooksRepository


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/tenant", status_code=status.HTTP_200_OK, response_model=TenantRead)
async def get_tenant(db: AsyncSession = Depends(get_db)) -> TenantRead:
    # this should take some query params, sorting and paging params...
    wallet_id = context.get("TENANT_WALLET_ID")
    if not wallet_id:
        raise HTTPException(
            status_code=403,
            detail="Error not authenticated",
        )
    repo = TenantsRepository(db_session=db)
    item = await repo.get_by_wallet_id(wallet_id)
    return item


@router.get("/tenant/issuer", status_code=status.HTTP_200_OK, response_model=TenantRead)
async def get_tenant_issuer(db: AsyncSession = Depends(get_db)) -> TenantRead:
    # this should take some query params, sorting and paging params...
    wallet_id = context.get("TENANT_WALLET_ID")
    if not wallet_id:
        raise HTTPException(
            status_code=403,
            detail="Error not authenticated",
        )
    repo = TenantsRepository(db_session=db)
    item = await repo.get_by_wallet_id(wallet_id)
    return item


@router.get(
    "/webhooks", status_code=status.HTTP_200_OK, response_model=List[TenantWebhookRead]
)
async def get_tenant_webhooks(
    db: AsyncSession = Depends(get_db),
) -> List[TenantWebhookRead]:
    # this should take some query params, sorting and paging params...
    wallet_id = context.get("TENANT_WALLET_ID")
    if not wallet_id:
        raise HTTPException(
            status_code=403,
            detail="Error not authenticated",
        )
    repo = TenantWebhooksRepository(db_session=db)
    items = await repo.find_by_wallet_id(wallet_id)
    return items
