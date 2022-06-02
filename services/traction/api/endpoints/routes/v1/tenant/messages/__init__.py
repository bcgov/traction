from fastapi import APIRouter

from .messages import router as messages
from .message import router as message

messages_router = APIRouter()
messages_router.include_router(messages, tags=[])
messages_router.include_router(message, tags=[])
