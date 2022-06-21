from fastapi import APIRouter

from .issuer import router as issuer
from .self import router as me
from .configuration import router as conf

admin_router = APIRouter()
admin_router.include_router(me, tags=[])
admin_router.include_router(issuer, tags=[])
admin_router.include_router(conf, tags=[])
