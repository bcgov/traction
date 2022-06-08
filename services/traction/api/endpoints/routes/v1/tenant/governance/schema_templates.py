import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from api.core.config import settings
from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.routes.v1.link_utils import build_list_links

from api.services.v1 import governance_service

from api.endpoints.models.v1.governance import (
    SchemaTemplateListResponse,
    SchemaTemplateListParameters,
    CreateSchemaTemplatePayload,
    CreateSchemaTemplateResponse,
    ImportSchemaTemplatePayload,
    ImportSchemaTemplateResponse,
    TemplateStatusType,
)
from api.tasks import SendCredDefRequestTask, SendSchemaRequestTask

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=SchemaTemplateListResponse
)
async def list_schema_templates(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    name: str | None = None,
    schema_id: str | None = None,
    schema_template_id: UUID | None = None,
    status: TemplateStatusType | None = None,
    tags: str | None = None,
    deleted: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> SchemaTemplateListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    parameters = SchemaTemplateListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        name=name,
        deleted=deleted,
        schema_id=schema_id,
        schema_template_id=schema_template_id,
        status=status,
        tags=tags,
    )
    items, total_count = await governance_service.list_schema_templates(
        db, tenant_id, wallet_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return SchemaTemplateListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post("/", status_code=status.HTTP_200_OK)
async def create_schema_template(
    payload: CreateSchemaTemplatePayload,
    db: AsyncSession = Depends(get_db),
) -> CreateSchemaTemplateResponse:
    """
    Create a new schema and/or credential definition.

    "schema_definition", defines the new schema.
    If "credential_definition" is provided, create a credential definition.
    """
    logger.info("> create_schema_template()")
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    logger.debug(f"wallet_id = {wallet_id}")
    logger.debug(f"tenant_id = {tenant_id}")

    item, c_t_item = await governance_service.create_schema_template(
        db, tenant_id, wallet_id, payload=payload
    )
    links = []  # TODO

    # this will kick off the call to the ledger and then event listeners will finish
    # populating the schema (and cred def) data.
    logger.debug("> > SendSchemaRequestTask.assign()")
    await SendSchemaRequestTask.assign(
        tenant_id, wallet_id, payload.schema_definition, item.schema_template_id
    )
    logger.debug("< < SendSchemaRequestTask.assign()")
    logger.debug(f"item = {item}")
    logger.debug(f"credential_template = {c_t_item}")
    logger.info("< create_schema_template()")
    return CreateSchemaTemplateResponse(
        item=item, credential_template=c_t_item, links=links
    )


@router.post("/import", status_code=status.HTTP_200_OK)
async def import_schema_template(
    payload: ImportSchemaTemplatePayload,
    db: AsyncSession = Depends(get_db),
) -> ImportSchemaTemplateResponse:
    """
    Import an existing public schema and optionally create a credential definition.

    "schema_id" is the ledger's schema id.
    If "credential_definition" is provided, create a credential definition.
    """
    logger.info("> import_schema_template()")
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    logger.debug(f"wallet_id = {wallet_id}")
    logger.debug(f"tenant_id = {tenant_id}")

    item, c_t_item = await governance_service.import_schema_template(
        db, tenant_id, wallet_id, payload=payload
    )
    links = []  # TODO

    # this will kick off the call to the ledger and then event listeners will finish
    # populating the cred def
    if c_t_item:
        logger.debug("> > SendCredDefRequestTask.assign()")
        await SendCredDefRequestTask.assign(
            tenant_id, wallet_id, c_t_item.credential_template_id
        )
        logger.debug("< < SendCredDefRequestTask.assign()")

    logger.debug(f"item = {item}")
    logger.debug(f"credential_template = {c_t_item}")
    logger.info("< import_schema_template()")
    return ImportSchemaTemplateResponse(
        item=item, credential_template=c_t_item, links=links
    )
