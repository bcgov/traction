from fastapi import APIRouter

from .contacts import router as contacts
from .events import router as events
from .holder import router as holder
from .issuer import router as issuer
from .messages import router as messages
from .schemas import router as schemas
from .verifier import router as verifier

router = APIRouter()
router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
router.include_router(holder.router, prefix="/holder", tags=["holder"])
router.include_router(issuer.router, prefix="/issuer", tags=["issuer"])
router.include_router(verifier.router, prefix="/verifier", tags=["verifier"])
router.include_router(schemas.router, prefix="/schemas", tags=["schemas"])
router.include_router(messages.router, prefix="/messages", tags=["messages"])
router.include_router(events.router, prefix="/events", tags=["events"])
