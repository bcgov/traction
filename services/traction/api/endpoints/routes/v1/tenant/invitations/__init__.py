from fastapi import APIRouter

from .invitations import router as invitations

invitations_router = APIRouter()
invitations_router.include_router(invitations, tags=[])
