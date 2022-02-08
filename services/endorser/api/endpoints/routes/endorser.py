import logging
from typing import List

from fastapi import APIRouter
from starlette import status

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/transactions", status_code=status.HTTP_200_OK, response_model=List[dict])
async def get_transactions() -> List[dict]:
    # this should take some query params, sorting and paging params...
    return [{}]
