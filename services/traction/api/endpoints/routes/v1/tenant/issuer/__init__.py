from fastapi import APIRouter

from .issuer import router as issuer
from .credentials import router as issuer_creds

issuer_router = APIRouter()
issuer_router.include_router(issuer, tags=[])
issuer_router.include_router(issuer_creds, tags=[])
