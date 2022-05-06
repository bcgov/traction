from fastapi import APIRouter

from .issuer import router as issuer

admin_router = APIRouter()
admin_router.include_router(issuer, tags=[], prefix="/issuer")
