from fastapi import APIRouter

from .credentials import router as credentials_router

router = APIRouter()
router.include_router(credentials_router, prefix="/credentials", tags=["credentials"])
