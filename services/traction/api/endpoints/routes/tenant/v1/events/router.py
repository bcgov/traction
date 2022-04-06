from fastapi import APIRouter

from .config import router as config
from .event import router as event
from .events import router as events

router = APIRouter()
router.include_router(events)
router.include_router(event)
router.include_router(config, tags=["config"])
