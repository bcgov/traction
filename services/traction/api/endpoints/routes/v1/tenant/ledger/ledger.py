import logging
import json
from uuid import UUID
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

from api.db.repositories.tenant_schemas import TenantSchemasRepository
from api.db.models.tenant_schema import (
    TenantSchemaRead,
    TenantSchemaCreate,
    TenantSchemaUpdate,
)

from api.db.models.tenant_workflow import (
    TenantWorkflowRead,
)

from api.endpoints.models.tenant_workflow import (
    TenantWorkflowTypeType,
    TenantWorkflowStateType,
)
from api.db.repositories.tenant_workflows import TenantWorkflowsRepository
from api.services.tenant_workflows import create_workflow
from api.services.base import BaseWorkflow


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
    schema_repo = TenantSchemasRepository(db_session=db)
    tenant_schema = None
    tenant_schemas = await schema_repo.find_by_wallet_id(wallet_id)
    for schema in tenant_schemas:
        if schema_request:
            if cred_def_tag:
                if (
                    schema_request.schema_name == schema.schema_name
                    and schema_request.schema_version == schema.schema_version
                    and cred_def_tag == schema.cred_def_tag
                ):
                    tenant_schema = schema
                    break
            else:
                if (
                    schema_request.schema_name == schema.schema_name
                    and schema_request.schema_version == schema.schema_version
                ):
                    tenant_schema = schema
                    break
        elif schema_id:
            if cred_def_tag:
                if (
                    schema_id == schema.schema_id
                    and cred_def_tag == schema.cred_def_tag
                ):
                    tenant_schema = schema
                    break
            else:
                if schema_id == schema.schema_id:
                    tenant_schema = schema
                    break
        else:
            # exception!
            raise Exception(
                "Need to provide either schema_id or schema name/version/attributes."
            )
    logger.debug(f">>> Existing tenant_schema: {tenant_schema}")
    if not tenant_schema:
        tenant_schema = TenantSchemaCreate(
            tenant_id=tenant_id,
            wallet_id=wallet_id,
            workflow_id=None,
            schema_id=schema_id,
            schema_name=schema_request.schema_name if schema_request else None,
            schema_version=schema_request.schema_version if schema_request else None,
            schema_attrs=json.dumps(schema_request.attributes)
            if schema_request
            else None,
            schema_state=TenantWorkflowStateType.pending
            if schema_request
            else TenantWorkflowStateType.completed,
            cred_def_tag=cred_def_tag,
            cred_def_state=TenantWorkflowStateType.pending if cred_def_tag else None,
            cred_revocation=revocable,
            cred_revoc_reg_size=revoc_reg_size if revocable else None,
            revoc_reg_state=TenantWorkflowStateType.pending if revocable else None,
        )
        tenant_schema = await schema_repo.create(tenant_schema)
        logger.debug(f">>> Created new tenant_schema: {tenant_schema}")
    workflow_repo = TenantWorkflowsRepository(db_session=db)
    tenant_workflow = None
    if tenant_schema.workflow_id:
        tenant_workflow = await workflow_repo.get_by_id(tenant_schema.workflow_id)

    else:
        # create workflow and update schema record
        tenant_workflow = await create_workflow(
            wallet_id,
            TenantWorkflowTypeType.schema,
            db,
            error_if_wf_exists=False,
            start_workflow=False,
        )
        logger.debug(f">>> Created tenant_workflow: {tenant_workflow}")
        schema_update = TenantSchemaUpdate(
            id=tenant_schema.id,
            workflow_id=tenant_workflow.id,
            schema_id=tenant_schema.schema_id,
            schema_state=tenant_schema.schema_state,
            cred_def_state=tenant_schema.cred_def_state,
            revoc_reg_state=tenant_schema.revoc_reg_state,
        )
        tenant_schema = await schema_repo.update(schema_update)
        logger.debug(f">>> Updated tenant_schema: {tenant_schema}")

        # start workflow
        tenant_workflow = await BaseWorkflow.next_workflow_step(
            db, tenant_workflow=tenant_workflow
        )
        logger.debug(f">>> Updated tenant_workflow: {tenant_workflow}")

        # get updated issuer info (should have workflow id etc.)
        tenant_schema = await schema_repo.get_by_id(tenant_schema.id)
        logger.debug(f">>> Updated (final) tenant_schema: {tenant_schema}")

    schema = TenantSchemaData(
        schema_data=tenant_schema,
        workflow=tenant_workflow,
    )
    return schema


###
