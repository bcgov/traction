import logging
from typing import List
from uuid import UUID


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db

from api.endpoints.models.v1.models import (
    CredentialDefinition,
    CredentialDefinitionList,
    CreateCredentialDefinitionPayload,
    CreateCredentialDefinitionResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/", status_code=status.HTTP_200_OK, response_model=CredentialDefinitionList
)
async def list_credential_definitions(
    db: AsyncSession = Depends(get_db),
) -> CredentialDefinitionList:
    raise NotImplementedError


@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=CreateCredentialDefinitionResponse,
)
async def create_credential_definition(
    payload: CreateCredentialDefinitionPayload,
    db: AsyncSession = Depends(get_db),
) -> CreateCredentialDefinitionResponse:
    raise NotImplementedError


@router.delete(
    "/{credential_definition_id}",
    status_code=status.HTTP_200_OK,
    response_model=CredentialDefinition,
)
async def delete_credential_definition(
    credential_definition_id: UUID, db: AsyncSession = Depends(get_db)
) -> CredentialDefinition:
    raise NotImplementedError
