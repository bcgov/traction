from fastapi import APIRouter

from .credentials import router as credentials
from .credential_definitions import router as credential_definitions

router = APIRouter()
router.include_router(credentials, prefix="/credentials", tags=["credentials"])
router.include_router(
    credential_definitions, prefix="/credential-definitions", tags=["credentials"]
)
