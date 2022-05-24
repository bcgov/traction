import logging
from uuid import UUID

from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from api.endpoints.dependencies.db import get_db
from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.models.v1.issuer import IssuedCredentialGetResponse
from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import issuer_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{issued_credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=IssuedCredentialGetResponse,
)
async def get_issued_credential(
    request: Request,
    issued_credential_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
    timeline: bool | None = False,
    db: AsyncSession = Depends(get_db),
) -> IssuedCredentialGetResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await issuer_service.get_issued_credential(
        db,
        tenant_id,
        wallet_id,
        issued_credential_id=issued_credential_id,
        acapy=acapy,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    timeline_items = []
    if timeline:
        timeline_items = await issuer_service.get_issued_credential_timeline(
            db, issued_credential_id
        )

    return IssuedCredentialGetResponse(item=item, links=links, timeline=timeline_items)
