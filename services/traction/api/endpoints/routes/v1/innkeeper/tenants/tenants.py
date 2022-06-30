import logging


from fastapi import APIRouter
from starlette import status

from api.endpoints.models.v1.innkeeper import CheckInResponse, CheckInPayload
from api.services.v1 import innkeeper_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/check-in",
    status_code=status.HTTP_200_OK,
    response_model=CheckInResponse,
)
async def check_in_tenant(payload: CheckInPayload) -> CheckInResponse:
    item = await innkeeper_service.check_in_tenant(payload=payload)

    links = []  # TODO: determine useful links for /check-in

    return CheckInResponse(item=item, links=links)
