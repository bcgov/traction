from fastapi import APIRouter

from .credentials import router as issuer_creds

issuer_router = APIRouter()
issuer_router.include_router(issuer_creds, prefix="/credentials", tags=[])
