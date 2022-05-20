from fastapi import APIRouter

from .schemas import router as schemas
from .schema import router as schema

governance_router = APIRouter()
governance_router.include_router(schemas, tags=[], prefix="/schemas")
governance_router.include_router(schema, tags=[], prefix="/schemas")
