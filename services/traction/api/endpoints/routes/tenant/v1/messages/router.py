from fastapi import APIRouter

from .messages import router as messages

router = APIRouter()
router.include_router(messages)
