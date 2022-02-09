import logging
from fastapi import APIRouter
from starlette import status


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def receive_webhook():
    return {"message": "got webhook"}
