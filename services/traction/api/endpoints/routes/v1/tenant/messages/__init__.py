from fastapi import APIRouter

from api.endpoints.routes.v1.tenant.context_route import TenantContextRoute

from .messages import router as messages
from .message import router as message

messages_router = APIRouter(route_class=TenantContextRoute)
messages_router.include_router(messages, tags=[])
messages_router.include_router(message, tags=[])
