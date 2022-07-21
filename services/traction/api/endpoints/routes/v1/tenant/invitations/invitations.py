import logging

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.core.config import settings
from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context

from api.endpoints.routes.v1.link_utils import build_list_links
from api.endpoints.models.v1.invitations import (
    InvitationListResponse,
    InvitationListParameters,
    CreateMultiUseInvitationResponse,
    CreateMultiUseInvitationPayload,
)
from api.services.v1 import invitations_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=InvitationListResponse)
async def list_invitations(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    acapy: bool | None = False,
    name: str | None = None,
    tags: str | None = None,
    deleted: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> InvitationListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    parameters = InvitationListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        acapy=acapy,
        name=name,
        deleted=deleted,
        tags=tags,
    )
    items, total_count = await invitations_service.list_invitations(
        db, tenant_id, wallet_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return InvitationListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post(
    "/create-multi-use-invitation",
    status_code=status.HTTP_200_OK,
    response_model=CreateMultiUseInvitationResponse,
)
async def create_multi_use_invitation(
    payload: CreateMultiUseInvitationPayload,
    db: AsyncSession = Depends(get_db),
) -> CreateMultiUseInvitationResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")
    (item, invitation_url,) = await invitations_service.create_multi_use_invitation(
        db, tenant_id, wallet_id, payload=payload
    )
    links = []  # TODO
    return CreateMultiUseInvitationResponse(
        item=item, invitation_url=invitation_url, links=links
    )
