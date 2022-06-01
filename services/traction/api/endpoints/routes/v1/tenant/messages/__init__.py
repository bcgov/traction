from fastapi import APIRouter

from .messages import router as messages

messages_router = APIRouter()
messages_router.include_router(messages, tags=[])
