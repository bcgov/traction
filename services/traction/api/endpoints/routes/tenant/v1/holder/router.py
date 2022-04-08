from fastapi import APIRouter

from .credentials import router as credentials
from .presentations import router as presentations

router = APIRouter()
router.include_router(credentials, prefix="/credentials", tags=["credentials"])
router.include_router(presentations, prefix="/presentations", tags=["presentations"])
