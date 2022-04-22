import logging
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from pydantic import BaseModel


from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.contacts import ContactGetResponse
from api.endpoints.models.tenant_schema import TenantSchemaRequest
from api.db.models.tenant_issuer import TenantIssuerRead
from api.db.models.tenant_schema import (
    TenantSchemaRead,
)

from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)
from api.services.v1 import ledger_service


router = APIRouter()
logger = logging.getLogger(__name__)


class TenantIssuerData(BaseModel):
    issuer: TenantIssuerRead | None = None
    workflow: TenantWorkflowRead | None = None


class TenantSchemaData(BaseModel):
    schema_data: TenantSchemaRead | None = None
    workflow: TenantWorkflowRead | None = None


@router.post(
    "/schema", status_code=status.HTTP_200_OK, response_model=ContactGetResponse
)
### Method moved from v0
async def create_tenant_schema(
    schema_request: TenantSchemaRequest | None = None,
    schema_id: str | None = None,
    cred_def_tag: str | None = None,
    revocable: bool | None = False,
    revoc_reg_size: int | None = 1000,
    db: AsyncSession = Depends(get_db),
) -> List[TenantSchemaData]:
    """
    Create a new schema and/or credential definition.

    If "schema" is provided, create a new schema.
    If "schema_id" is provided, use an existing schema.
    If "cred_def_tag" is provided, create a credential definition (which can be for a
    new or existing schema).
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    return ledger_service.create_tenant_schema(
        db,
        wallet_id,
        tenant_id,
        schema_request,
        schema_id,
        cred_def_tag,
        revocable,
        revoc_reg_size,
    )


###
