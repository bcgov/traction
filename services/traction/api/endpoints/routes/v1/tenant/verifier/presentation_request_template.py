import logging
from uuid import UUID

from fastapi import APIRouter, Request

from starlette import status


from api.endpoints.dependencies.tenant_security import get_from_context

from api.endpoints.models.v1.verifier import (
    GetPresentationRequestTemplateResponse,
    UpdatePresentationRequestTemplatePayload,
    GetVerifierPresentationResponse,
    PresentationRequestFromTemplatePayload,
)
from api.endpoints.routes.v1.link_utils import build_item_links
from api.services.v1 import verifier_service
from api.tasks import SendPresentProofTask

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{presentation_request_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetPresentationRequestTemplateResponse,
)
async def get_presentation_request_template(
    request: Request,
    presentation_request_template_id: UUID,
    deleted: bool | None = False,
) -> GetPresentationRequestTemplateResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await verifier_service.get_presentation_request_template(
        tenant_id,
        wallet_id,
        presentation_request_template_id=presentation_request_template_id,
        deleted=deleted,
    )

    links = build_item_links(str(request.url), item)

    return GetPresentationRequestTemplateResponse(
        item=item,
        links=links,
    )


@router.put(
    "/{presentation_request_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetPresentationRequestTemplateResponse,
)
async def update_presentation_request_template(
    request: Request,
    presentation_request_template_id: UUID,
    payload: UpdatePresentationRequestTemplatePayload,
) -> GetPresentationRequestTemplateResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await verifier_service.update_presentation_request_template(
        tenant_id,
        wallet_id,
        presentation_request_template_id=presentation_request_template_id,
        payload=payload,
    )

    links = build_item_links(str(request.url), item)

    return GetPresentationRequestTemplateResponse(item=item, link=links)


@router.delete(
    "/{presentation_request_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=GetPresentationRequestTemplateResponse,
)
async def delete_presentation_request_template(
    request: Request,
    presentation_request_template_id: UUID,
) -> GetPresentationRequestTemplateResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await verifier_service.delete_presentation_request_template(
        tenant_id,
        wallet_id,
        presentation_request_template_id=presentation_request_template_id,
    )

    links = build_item_links(str(request.url), item)

    return GetPresentationRequestTemplateResponse(item=item, link=links)


@router.post(
    "/{presentation_request_template_id}/send-request",
    status_code=status.HTTP_200_OK,
    response_model=GetVerifierPresentationResponse,
)
async def send_request_from_template(
    request: Request,
    presentation_request_template_id: UUID,
    payload: PresentationRequestFromTemplatePayload,
) -> GetVerifierPresentationResponse:
    """The Aries protocol for presenting proof to another agent, this endpoint only
    supports the aries protocol found here
    https://github.com/hyperledger/aries-rfcs/tree/main/features/0037-present-proof."""
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    # TODO: this is pretty much the same code that is in the adhoc route, refactor?
    (
        item,
        proof_request,
    ) = await verifier_service.make_verifier_presentation_from_template(
        tenant_id, wallet_id, presentation_request_template_id, payload
    )
    task_payload = {
        "verifier_presentation_id": item.verifier_presentation_id,
        "contact_id": item.contact.contact_id,
        "proof_request": proof_request,
    }
    await SendPresentProofTask.assign(tenant_id, wallet_id, task_payload)

    links = []  # TODO: set the links for issue new credential

    return GetVerifierPresentationResponse(item=item, links=links)
