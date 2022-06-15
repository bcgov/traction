import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.services.v1 import verifier_service

from api.endpoints.dependencies.tenant_security import get_from_context
from api.endpoints.dependencies.db import get_db

from api.endpoints.models.v1.verifier import (
    PresentationRequestListResponse,
    GetPresentationRequestResponse,
    CreatePresentationRequestPayload,
)
from api.endpoints.models.credentials import PresentCredentialProtocolType
from api.tasks.present_proof_tasks import SendPresentProofTask


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=PresentationRequestListResponse)
async def list_issued_credentials(
    db: AsyncSession = Depends(get_db),
) -> PresentationRequestListResponse:
    # TODO: search and paging parameters...
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    items, total_count = await verifier_service.list_presentation_requests(
        db, tenant_id, wallet_id
    )

    links = []  # TODO: set the paging links

    return PresentationRequestListResponse(
        items=items, count=len(items), total=total_count, links=links
    )


@router.post(
    "/v1/",
    status_code=status.HTTP_201_CREATED,
    response_model=GetPresentationRequestResponse,
)
async def verifer_new_presentation_request(
    payload: CreatePresentationRequestPayload,
    db: AsyncSession = Depends(get_db),
) -> GetPresentationRequestResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    # logger.warn(payload)
    item = await verifier_service.make_presentation_request(
        db, tenant_id, wallet_id, PresentCredentialProtocolType.v10, payload
    )
    task_payload = {
        "v_presentation_request_id": item.v_presentation_request_id,
        "contact_id": item.contact_id,
        "proof_request": item.proof_request,
    }
    await SendPresentProofTask.assign(tenant_id, wallet_id, task_payload)

    links = []  # TODO: set the links for issue new credential

    return GetPresentationRequestResponse(item=item, links=links)
