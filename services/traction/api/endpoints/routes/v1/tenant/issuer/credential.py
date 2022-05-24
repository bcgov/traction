import logging
from uuid import UUID

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.issuer import (
    IssuerCredentialGetResponse,
    UpdateIssuerCredentialPayload,
    UpdateIssuerCredentialResponse,
)
from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import issuer_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{issuer_credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=IssuerCredentialGetResponse,
)
async def get_issuer_credential(
    request: Request,
    issuer_credential_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
    timeline: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> IssuerCredentialGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await issuer_service.get_issuer_credential(
        db,
        tenant_id,
        wallet_id,
        issuer_credential_id=issuer_credential_id,
        acapy=acapy,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    timeline_items = []
    if timeline:
        timeline_items = await issuer_service.get_issuer_credential_timeline(
            db, issuer_credential_id
        )

    return IssuerCredentialGetResponse(item=item, links=links, timeline=timeline_items)


@router.put(
    "/{issuer_credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=UpdateIssuerCredentialResponse,
)
async def update_issuer_credential(
    request: Request,
    issuer_credential_id: UUID,
    payload: UpdateIssuerCredentialPayload,
    db: AsyncSession = Depends(get_db),
) -> UpdateIssuerCredentialResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await issuer_service.update_issuer_credential(
        db,
        tenant_id,
        wallet_id,
        issuer_credential_id=issuer_credential_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return UpdateIssuerCredentialResponse(item=item, link=links)


@router.delete(
    "/{issuer_credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=IssuerCredentialGetResponse,
)
async def delete_issuer_credential(
    request: Request,
    issuer_credential_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> IssuerCredentialGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await issuer_service.delete_issuer_credential(
        db,
        tenant_id,
        wallet_id,
        issuer_credential_id=issuer_credential_id,
    )

    links = build_item_links(str(request.url), item)

    return IssuerCredentialGetResponse(item=item, link=links)
