from fastapi import APIRouter

from .credentials import router as holder_creds
from .credential import router as holder_cred

holder_router = APIRouter()
holder_router.include_router(holder_creds, prefix="/credentials", tags=[])
holder_router.include_router(holder_cred, prefix="/credentials", tags=[])
