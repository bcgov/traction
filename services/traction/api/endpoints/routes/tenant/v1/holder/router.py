from fastapi import APIRouter

from .credentials import router as credentials_router
from .presentations import router as presentations_router

router = APIRouter()
router.include_router(credentials_router, prefix="/credentials", tags=["credentials"])
router.include_router(
    presentations_router, prefix="/presentations", tags=["presentations"]
)
