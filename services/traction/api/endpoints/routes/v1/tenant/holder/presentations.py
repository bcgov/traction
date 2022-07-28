import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status
from starlette.requests import Request

from api.core.config import settings
from api.endpoints.models.v1.holder import (
    HolderPresentationStatusType,
    HolderPresentationListParameters,
    HolderPresentationListResponse,
    HolderSendProposalPayload,
    HolderSendProposalResponse,
)
from api.endpoints.routes.v1.link_utils import build_list_links

from api.endpoints.dependencies.tenant_security import get_from_context
from api.services.v1 import holder_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=HolderPresentationListResponse
)
async def list_holder_presentations(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    name: str | None = None,
    contact_id: UUID | None = None,
    external_reference_id: str | None = None,
    status: HolderPresentationStatusType | None = None,
    acapy: bool | None = None,
    tags: str | None = None,
    deleted: bool | None = False,
) -> HolderPresentationListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    parameters = HolderPresentationListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        name=name,
        deleted=deleted,
        contact_id=contact_id,
        external_reference_id=external_reference_id,
        status=status,
        acapy=acapy,
        tags=tags,
    )
    items, total_count = await holder_service.list_holder_presentations(
        tenant_id, wallet_id, parameters
    )

    links = build_list_links(total_count, parameters)

    return HolderPresentationListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post("/send-proposal", status_code=status.HTTP_200_OK)
async def send_proposal(
    payload: HolderSendProposalPayload,
    save_in_traction: bool | None = False,
) -> HolderSendProposalResponse:
    """Holder - Send Proposal

    This allows a holder to send a verifier a proposal of proof.

    Refer to the following RFC for more information on the flow:
    https://github.com/hyperledger/aries-rfcs/tree/main/features/0037-present-proof#propose-presentation

    For the content structure the presentation_proposal attributes and predicates:
    https://github.com/hyperledger/aries-rfcs/tree/main/features/0037-present-proof#presentation-preview
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await holder_service.send_proposal(tenant_id, wallet_id, payload=payload)
    links = []  # TODO
    return HolderSendProposalResponse(item=item, links=links)
