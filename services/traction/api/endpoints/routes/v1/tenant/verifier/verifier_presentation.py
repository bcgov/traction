import logging
import uuid

from fastapi import APIRouter

from api.services.v1 import verifier_service

from api.endpoints.dependencies.tenant_context import get_from_context

from api.endpoints.models.v1.verifier import (
    GetVerifierPresentationResponse,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{verifier_presentation_id}", response_model=GetVerifierPresentationResponse
)
async def get_verifier_presentation(
    verifier_presentation_id: uuid.UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> GetVerifierPresentationResponse:
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await verifier_service.get_presentation_request(
        tenant_id, wallet_id, verifier_presentation_id, acapy=acapy, deleted=deleted
    )

    return GetVerifierPresentationResponse(item=item, links=[])
