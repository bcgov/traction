from fastapi import APIRouter

from .schemas import router as schemas

governance_router = APIRouter()
governance_router.include_router(schemas, tags=[], prefix="/schemas")
