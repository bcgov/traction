from fastapi import APIRouter

from .issuer import router as issuer
from .self import router as me

admin_router = APIRouter()
admin_router.include_router(me, tags=[])
admin_router.include_router(issuer, tags=[])
