import logging
from uuid import UUID

from fastapi import APIRouter
from fastapi.openapi.models import Response
from starlette import status
from starlette.requests import Request


from api.endpoints.models.v1.messages import (
    UpdateMessagePayload,
)

from api.endpoints.routes.v1.tenant.deprecate import sunset_response


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response,
    deprecated=True,
)
async def get_message(
    request: Request,
    message_id: UUID,
    acapy: bool | None = False,
    deleted: bool | None = False,
) -> Response:
    return sunset_response


@router.put(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response,
    deprecated=True,
)
async def update_message(
    request: Request,
    message_id: UUID,
    payload: UpdateMessagePayload,
) -> Response:
    return sunset_response


@router.delete(
    "/{message_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response,
    deprecated=True,
)
async def delete_message(
    request: Request,
    message_id: UUID,
) -> Response:
    return sunset_response
