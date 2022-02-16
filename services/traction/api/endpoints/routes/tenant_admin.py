import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette_context import context

from api.db.errors import DoesNotExist
from api.db.models.tenant import TenantRead
from api.db.models.tenant_issuer import TenantIssuerRead, TenantIssuerUpdate
from api.db.models.tenant_webhook import TenantWebhookRead
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.db.repositories.tenants import TenantsRepository
from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.db.repositories.tenant_webhooks import TenantWebhooksRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.endpoints.dependencies.db import get_db
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
)
from api.services.tenant_workflows import create_workflow


router = APIRouter()
logger = logging.getLogger(__name__)


class TenantIssuerData(BaseModel):
    issuer: TenantIssuerRead | None = None
    workflow: TenantWorkflowRead | None = None


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


@router.get(
    "/tenant/issuer", status_code=status.HTTP_200_OK, response_model=TenantIssuerData
)
async def get_tenant_issuer(db: AsyncSession = Depends(get_db)) -> TenantIssuerData:
    # this should take some query params, sorting and paging params...
    wallet_id = context.get("TENANT_WALLET_ID")
    if not wallet_id:
        raise HTTPException(
            status_code=403,
            detail="Error not authenticated",
        )
    issuer_repo = TenantIssuersRepository(db_session=db)
    tenant_issuer = await issuer_repo.get_by_wallet_id(wallet_id)
    tenant_workflow = None
    if tenant_issuer.workflow_id:
        try:
            workflow_repo = TenantWorkflowsRepository(db_session=db)
            tenant_workflow = await workflow_repo.get_by_id(tenant_issuer.workflow_id)
        except DoesNotExist:
            pass
    issuer = TenantIssuerData(
        issuer=tenant_issuer,
        workflow=tenant_workflow,
    )
    return issuer


@router.post(
    "/tenant/issuer", status_code=status.HTTP_200_OK, response_model=TenantIssuerData
)
async def make_tenant_issuer(db: AsyncSession = Depends(get_db)) -> TenantIssuerData:
    # this should kick off the process of upgrading a tenant to be an "issuer"
    wallet_id = context.get("TENANT_WALLET_ID")
    if not wallet_id:
        raise HTTPException(
            status_code=403,
            detail="Error not authenticated",
        )
    issuer_repo = TenantIssuersRepository(db_session=db)
    tenant_issuer = await issuer_repo.get_by_wallet_id(wallet_id)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    tenant_workflow = None
    if tenant_issuer.workflow_id:
        tenant_workflow = await workflow_repo.get_by_id(tenant_issuer.workflow_id)

    else:
        # create workflow and update issuer record
        tenant_workflow = await create_workflow(
            wallet_id,
            TenantWorkflowTypeType.issuer,
            db,
        )
        update_issuer = TenantIssuerUpdate(
            id=tenant_issuer.id,
            workflow_id=tenant_workflow.id,
        )
        tenant_issuer = await issuer_repo.update(update_issuer)

    issuer = TenantIssuerData(
        issuer=tenant_issuer,
        workflow=tenant_workflow,
    )

    return issuer


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
