import logging

from fastapi import APIRouter

from starlette import status

from api.endpoints.dependencies.tenant_context import get_from_context

from api.endpoints.models.v1.tenant import TenantGetResponse

from api.services.v1 import tenant_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/make-issuer", status_code=status.HTTP_200_OK, response_model=TenantGetResponse
)
async def initialize_issuer() -> TenantGetResponse:
    """
    If the innkeeper has authorized your tenant to become an issuer, initialize
    here to write a endorsed public did the configured Hyperledger-Indy service
    """
    wallet_id = get_from_context("TENANT_WALLET_ID")
    tenant_id = get_from_context("TENANT_ID")

    item = await tenant_service.make_issuer(
        tenant_id,
        wallet_id,
    )

    links = []  # TODO: determine useful links for /make-issuer

    return TenantGetResponse(item=item, links=links)
