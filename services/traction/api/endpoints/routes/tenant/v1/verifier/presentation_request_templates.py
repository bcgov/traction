import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db


from api.endpoints.models.v1.models import (
    CreatePresentationRequestTemplatePayload,
    PresentationRequestTemplate,
    UpdatePresentationRequestTemplatePayload,
    PresentationRequestTemplateList,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=PresentationRequestTemplateList,
)
async def list_presentation_request_templates(
    limit: Optional[int],
    marker: Optional[UUID],
    tags: Optional[str],
    db: AsyncSession = Depends(get_db),
) -> PresentationRequestTemplateList:
    raise NotImplementedError


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=PresentationRequestTemplate
)
async def create_presentation_request_template(
    payload: CreatePresentationRequestTemplatePayload,
    db: AsyncSession = Depends(get_db),
) -> PresentationRequestTemplate:
    raise NotImplementedError


@router.get(
    "/{presentation_request_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=PresentationRequestTemplate,
)
async def get_presentation_request_template(
    presentation_request_template_id: UUID, db: AsyncSession = Depends(get_db)
) -> PresentationRequestTemplate:
    raise NotImplementedError


@router.put(
    "/{presentation_request_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=PresentationRequestTemplate,
)
async def update_presentation_request_template(
    presentation_request_template_id: UUID,
    payload: UpdatePresentationRequestTemplatePayload,
    db: AsyncSession = Depends(get_db),
) -> PresentationRequestTemplate:
    raise NotImplementedError


@router.delete(
    "/{presentation_request_template_id}",
    status_code=status.HTTP_200_OK,
    response_model=PresentationRequestTemplate,
)
async def delete_presentation_request_template(
    presentation_request_template_id: UUID, db: AsyncSession = Depends(get_db)
) -> PresentationRequestTemplate:
    raise NotImplementedError
