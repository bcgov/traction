from fastapi import APIRouter

from .credentials import router as issuer_creds
from .credential import router as issuer_cred

issuer_router = APIRouter()
issuer_router.include_router(issuer_creds, prefix="/credentials", tags=[])
issuer_router.include_router(issuer_cred, prefix="/credentials", tags=[])
