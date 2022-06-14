import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.governance import (
    SchemaTemplateGetResponse,
    UpdateSchemaTemplateResponse,
    UpdateSchemaTemplatePayload,
)
from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import governance_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{schema_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=SchemaTemplateGetResponse,
)
async def get_schema_template(
    request: Request,
    schema_template_id: UUID,
    deleted: bool | None = False,
    timeline: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> SchemaTemplateGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await governance_service.get_schema_template(
        db,
        tenant_id,
        wallet_id,
        schema_template_id=schema_template_id,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    timeline_items = []
    if timeline:
        timeline_items = await governance_service.get_schema_template_timeline(
            db, schema_template_id
        )

    return SchemaTemplateGetResponse(item=item, links=links, timeline=timeline_items)


@router.put(
    "/{schema_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateSchemaTemplateResponse,
)
async def update_schema_template(
    request: Request,
    schema_template_id: UUID,
    payload: UpdateSchemaTemplatePayload,
    db: AsyncSession = Depends(get_db),
) -> UpdateSchemaTemplateResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await governance_service.update_schema_template(
        db, tenant_id, wallet_id, schema_template_id=schema_template_id, payload=payload
    )

    links = build_item_links(str(request.url), item)

    return UpdateSchemaTemplateResponse(item=item, link=links)


@router.delete(
    "/{schema_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=SchemaTemplateGetResponse,
)
async def delete_schema_template(
    request: Request,
    schema_template_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SchemaTemplateGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await governance_service.delete_schema_template(
        db, tenant_id, wallet_id, schema_template_id=schema_template_id
    )

    links = build_item_links(str(request.url), item)

    return SchemaTemplateGetResponse(item=item, link=links)
