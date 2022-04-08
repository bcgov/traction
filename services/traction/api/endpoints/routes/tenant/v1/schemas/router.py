from fastapi import APIRouter

from .schemas import router as schemas

router = APIRouter()
router.include_router(schemas)
