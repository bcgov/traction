from fastapi import APIRouter

from .schema_templates import router as schemas
from .schema_template import router as schema
from .credential_templates import router as credentials


governance_router = APIRouter()
governance_router.include_router(schemas, tags=[], prefix="/schema_templates")
governance_router.include_router(schema, tags=[], prefix="/schema_templates")
governance_router.include_router(credentials, tags=[], prefix="/credential_templates")
