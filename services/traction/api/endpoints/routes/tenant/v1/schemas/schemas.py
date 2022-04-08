import logging
from typing import Optional
from uuid import UUID


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db

from api.endpoints.models.v1.models import (
    TractionSchema,
    CreateTractionSchemaPayload,
    ImportTractionSchemaPayload,
    TractionSchemaList,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=TractionSchemaList)
async def list_schemas(
    limit: Optional[int],
    marker: Optional[UUID],
    tags: Optional[str],
    db: AsyncSession = Depends(get_db),
) -> TractionSchemaList:
    raise NotImplementedError


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=TractionSchema,
)
async def create_schema(
    payload: CreateTractionSchemaPayload,
    db: AsyncSession = Depends(get_db),
) -> TractionSchema:
    raise NotImplementedError


@router.post(
    "/import-schema",
    status_code=status.HTTP_200_OK,
    response_model=TractionSchema,
)
async def import_schema(
    payload: ImportTractionSchemaPayload,
    db: AsyncSession = Depends(get_db),
) -> TractionSchema:
    raise NotImplementedError
