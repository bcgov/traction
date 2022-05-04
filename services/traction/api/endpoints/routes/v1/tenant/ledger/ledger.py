import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pydantic import BaseModel


from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.tenant_schema import TenantSchemaRequest
from api.db.models.tenant_issuer import TenantIssuerRead
from api.db.models.tenant_schema import (
    TenantSchemaRead,
)

from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.services.v1 import ledger_service

from api.db.errors import DoesNotExist
from api.db.repositories.tenant_schemas import TenantSchemasRepository
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository

from api.endpoints.models.v1.ledger import SchemasListResponse, CreateSchemaPayload
from api.endpoints.routes.tenant_admin import TenantSchemaData

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/schemas", status_code=status.HTTP_200_OK, response_model=SchemasListResponse
)
async def get_tenant_schemas(
    db: AsyncSession = Depends(get_db),
) -> SchemasListResponse:
    # copy of v0 implementation from endpoints/routes/tenant_admin
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
    response = SchemasListResponse(
        items=schemas, count=len(schemas), total=len(schemas)
    )
    return response


@router.post("/schemas", status_code=status.HTTP_200_OK)
# Method moved from v0
async def create_tenant_schema(
    schema_request: CreateSchemaPayload | None = None,
    schema_id: str | None = None,
    cred_def_tag: str | None = None,
    revocable: bool | None = False,
    revoc_reg_size: int | None = 1000,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new schema and/or credential definition.

    If "schema" is provided, create a new schema.
    If "schema_id" is provided, use an existing schema.
    If "cred_def_tag" is provided, create a credential definition (which can be for a
    new or existing schema).
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    return await ledger_service.create_tenant_schema(
        db,
        wallet_id,
        tenant_id,
        schema_request,
        schema_id,
        cred_def_tag,
        revocable,
        revoc_reg_size,
    )
