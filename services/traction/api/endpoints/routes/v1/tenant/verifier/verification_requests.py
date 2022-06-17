import logging

from fastapi import APIRouter, Depends, Request
from starlette import status

from api.services.v1 import verifier_service
from api.core.config import settings

from api.endpoints.dependencies.tenant_security import get_from_context

from api.endpoints.models.v1.verifier import (
    VerificationRequestListResponse,
    GetVerificationRequestResponse,
    CreatePresentationRequestPayload,
    VerificationRequestListParameters,
)
from api.endpoints.models.credentials import PresentCredentialProtocolType
from api.tasks.present_proof_tasks import SendPresentProofTask


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=VerificationRequestListResponse)
async def list_verification_requests(
    request: Request,
    page_num: int | None = 1,
    page_size: int | None = settings.DEFAULT_PAGE_SIZE,
    acapy: bool | None = False,
    name: str | None = None,
    comment: str | None = None,
    version: str | None = None,
    deleted: bool | None = False,
    tags: str | None = None,
) -> VerificationRequestListResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    parameters = VerificationRequestListParameters(
        url=str(request.url),
        page_num=page_num,
        page_size=page_size,
        version=version,
        name=name,
        comment=comment,
        deleted=deleted,
        tags=tags,
    )

    items, total_count = await verifier_service.list_presentation_requests(
        tenant_id, wallet_id, parameters
    )

    links = []  # TODO: set the paging links

    return VerificationRequestListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post(
    "/v1/",
    status_code=status.HTTP_200_OK,
    response_model=GetVerificationRequestResponse,
)
async def new_verification_request(
    payload: CreatePresentationRequestPayload,
) -> GetVerificationRequestResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    # logger.warn(payload)
    item = await verifier_service.make_verification_request(
        tenant_id, wallet_id, PresentCredentialProtocolType.v10, payload
    )
    task_payload = {
        "verification_request_id": item.verification_request_id,
        "contact_id": item.contact_id,
        "proof_request": item.proof_request,
    }
    await SendPresentProofTask.assign(tenant_id, wallet_id, task_payload)

    links = []  # TODO: set the links for issue new credential

    return GetVerificationRequestResponse(item=item, links=links)
