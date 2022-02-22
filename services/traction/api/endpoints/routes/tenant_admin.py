import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette_context import context

from api.db.errors import DoesNotExist
from api.db.models.tenant import TenantRead
from api.db.models.tenant_issuer import TenantIssuerRead
from api.db.models.tenant_schema import TenantSchemaRead
from api.db.models.tenant_webhook import (
    TenantWebhookRead,
    TenantWebhookUpdate,
    TenantWebhookCreate,
)
from api.db.models.tenant_webhook_msg import TenantWebhookMsgRead
from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.db.repositories.tenants import TenantsRepository
from api.db.repositories.tenant_issuers import TenantIssuersRepository
from api.db.repositories.tenant_schemas import TenantSchemasRepository
from api.db.repositories.tenant_webhooks import TenantWebhooksRepository
from api.db.repositories.tenant_webhook_msgs import TenantWebhookMsgsRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.endpoints.dependencies.db import get_db
from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
)
from api.services.tenant_workflows import create_workflow

router = APIRouter()
logger = logging.getLogger(__name__)


def get_from_context(name: str):
    result = context.get(name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error not authenticated",
        )
    return result


class TenantIssuerData(BaseModel):
    issuer: TenantIssuerRead | None = None
    workflow: TenantWorkflowRead | None = None


class TenantSchemaData(BaseModel):
    schema_data: TenantSchemaRead | None = None
    workflow: TenantWorkflowRead | None = None


@router.get("/tenant", status_code=status.HTTP_200_OK, response_model=TenantRead)
async def get_tenant(db: AsyncSession = Depends(get_db)) -> TenantRead:
    # this should take some query params, sorting and paging params...
    wallet_id = get_from_context("TENANT_WALLET_ID")
    repo = TenantsRepository(db_session=db)
    item = await repo.get_by_wallet_id(wallet_id)
    return item


@router.get("/issuer", status_code=status.HTTP_200_OK, response_model=TenantIssuerData)
async def get_tenant_issuer(db: AsyncSession = Depends(get_db)) -> TenantIssuerData:
    # this should take some query params, sorting and paging params...
    wallet_id = get_from_context("TENANT_WALLET_ID")
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


@router.post("/issuer", status_code=status.HTTP_200_OK, response_model=TenantIssuerData)
async def make_tenant_issuer(db: AsyncSession = Depends(get_db)) -> TenantIssuerData:
    # this should kick off the process of upgrading a tenant to be an "issuer"
    wallet_id = get_from_context("TENANT_WALLET_ID")
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
        # get updated issuer info (should have workflow id and connection_id)
        tenant_issuer = await issuer_repo.get_by_wallet_id(wallet_id)

    issuer = TenantIssuerData(
        issuer=tenant_issuer,
        workflow=tenant_workflow,
    )

    return issuer


@router.get(
    "/schema", status_code=status.HTTP_200_OK, response_model=List[TenantSchemaData]
)
async def get_tenant_schemas(
    db: AsyncSession = Depends(get_db),
) -> List[TenantSchemaData]:
    # this should take some query params, sorting and paging params...
    wallet_id = get_from_context("TENANT_WALLET_ID")
    schema_repo = TenantSchemasRepository(db_session=db)
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    tenant_schemas = await schema_repo.find_by_wallet_id(wallet_id)
    schemas = []
    for tenant_schema in tenant_schemas:
        tenant_workflow = None
        if tenant_schema.workflow_id:
            try:
                tenant_workflow = await workflow_repo.get_by_id(
                    tenant_schema.workflow_id
                )
            except DoesNotExist:
                pass
        schema = TenantSchemaData(
            schema_data=tenant_schema,
            workflow=tenant_workflow,
        )
        schemas.append(schema)
    return schemas


@router.post("/schema", status_code=status.HTTP_200_OK, response_model=TenantSchemaData)
async def get_tenant_schemas(
    schema: dict | None = None,
    schema_id: str | None = None,
    cred_def_tag: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> List[TenantSchemaData]:
    schema = TenantSchemaData(
        schema_data=None,
        workflow=None,
    )
    return schema


@router.get(
    "/webhook/msgs",
    status_code=status.HTTP_200_OK,
    response_model=List[TenantWebhookMsgRead],
)
async def get_tenant_webhook_messages(
    db: AsyncSession = Depends(get_db),
) -> List[TenantWebhookMsgRead]:
    tenant_id = get_from_context("TENANT_ID")
    repo = TenantWebhookMsgsRepository(db_session=db)
    items = await repo.find_by_tenant_id(tenant_id)
    return items


@router.get(
    "/webhook", status_code=status.HTTP_200_OK, response_model=TenantWebhookRead
)
async def get_tenant_webhook(
    db: AsyncSession = Depends(get_db),
) -> TenantWebhookRead:
    tenant_id = get_from_context("TENANT_ID")
    repo = TenantWebhooksRepository(db_session=db)
    item = await repo.get_by_tenant_id(tenant_id)
    return item


@router.post(
    "/webhook", status_code=status.HTTP_201_CREATED, response_model=TenantWebhookRead
)
async def create_tenant_webhook(
    payload: TenantWebhookCreate,
    db: AsyncSession = Depends(get_db),
) -> TenantWebhookRead:
    tenant_id = get_from_context("TENANT_ID")
    repo = TenantWebhooksRepository(db_session=db)
    try:
        await repo.get_by_tenant_id(tenant_id)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tenant has a webhook, cannot create new webhook.",
        )
    except DoesNotExist:
        # let's add it
        payload.tenant_id = tenant_id
        webhook = await repo.create(payload)
        return webhook


@router.put(
    "/webhook", status_code=status.HTTP_200_OK, response_model=TenantWebhookRead
)
async def update_tenant_webhook(
    payload: TenantWebhookUpdate,
    db: AsyncSession = Depends(get_db),
) -> TenantWebhookRead:
    tenant_id = get_from_context("TENANT_ID")
    repo = TenantWebhooksRepository(db_session=db)
    current = await repo.get_by_tenant_id(tenant_id)
    if current.id == payload.id:
        item = await repo.update(payload)
        return item
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Webhook does not belong to this tenant",
        )
