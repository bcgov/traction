import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from api.endpoints.dependencies.db import get_db


from api.endpoints.models.v1.models import (
    IssuerConfig,
)


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", status_code=status.HTTP_200_OK, response_model=IssuerConfig)
async def get_issuer_config(db: AsyncSession = Depends(get_db)) -> IssuerConfig:
    raise NotImplementedError


@router.put(
    "/make-issuer", status_code=status.HTTP_202_ACCEPTED, response_model=IssuerConfig
)
async def make_tenant_an_issuer(db: AsyncSession = Depends(get_db)) -> None:
    raise NotImplementedError
