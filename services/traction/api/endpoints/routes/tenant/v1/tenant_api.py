from fastapi import APIRouter

from api.endpoints.routes.tenant.v1.contacts import router as contacts
from api.endpoints.routes.tenant.v1.events import router as events
from api.endpoints.routes.tenant.v1.holder import router as holder
from api.endpoints.routes.tenant.v1.issuer import router as issuer
from api.endpoints.routes.tenant.v1.messages import router as messages
from api.endpoints.routes.tenant.v1.profile import router as profile
from api.endpoints.routes.tenant.v1.verifier import router as verifier

tenant_router = APIRouter()
tenant_router.include_router(contacts.router, prefix="/contacts", tags=["contacts"])
tenant_router.include_router(holder.router, prefix="/holder", tags=["holder"])
tenant_router.include_router(issuer.router, prefix="/issuer", tags=["issuer"])
tenant_router.include_router(verifier.router, prefix="/verifier", tags=["verifier"])
tenant_router.include_router(messages.router, prefix="/messages", tags=["messages"])
tenant_router.include_router(events.router, prefix="/events", tags=["events"])
tenant_router.include_router(profile.router, prefix="/profile", tags=["profile"])
