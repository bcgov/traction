import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_context import get_from_context
from api.endpoints.models.v1.governance import (
    CredentialTemplateGetResponse,
    UpdateCredentialTemplateResponse,
    UpdateCredentialTemplatePayload,
)
from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import governance_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{credential_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=CredentialTemplateGetResponse,
)
async def get_credential_template(
    request: Request,
    credential_template_id: UUID,
    deleted: bool | None = False,
    timeline: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> CredentialTemplateGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await governance_service.get_credential_template(
        db,
        tenant_id,
        wallet_id,
        credential_template_id=credential_template_id,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    timeline_items = []
    if timeline:
        timeline_items = await governance_service.get_credential_template_timeline(
            db, credential_template_id
        )

    return CredentialTemplateGetResponse(
        item=item, links=links, timeline=timeline_items
    )


@router.put(
    "/{credential_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateCredentialTemplateResponse,
)
async def update_credential_template(
    request: Request,
    credential_template_id: UUID,
    payload: UpdateCredentialTemplatePayload,
    db: AsyncSession = Depends(get_db),
) -> UpdateCredentialTemplateResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await governance_service.update_credential_template(
        db,
        tenant_id,
        wallet_id,
        credential_template_id=credential_template_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return UpdateCredentialTemplateResponse(item=item, link=links)


@router.delete(
    "/{credential_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=CredentialTemplateGetResponse,
)
async def delete_credential_template(
    request: Request,
    credential_template_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> CredentialTemplateGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await governance_service.delete_credential_template(
        db, tenant_id, wallet_id, credential_template_id=credential_template_id
    )

    links = build_item_links(str(request.url), item)

    return CredentialTemplateGetResponse(item=item, link=links)
