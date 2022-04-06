from fastapi import APIRouter

from .config import router as config
from .profile import router as profile

router = APIRouter()
router.include_router(profile)
router.include_router(config, tags=["config"])
