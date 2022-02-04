import logging
import uuid

from jose import jwt
from starlette_context import context
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from api import acapy_utils as au
from api.core.config import settings


logger = logging.getLogger(__name__)


class JWTTFetchingMiddleware(BaseHTTPMiddleware):
    """Middleware to inject tenant JWT into context."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # extract the wallet_id and jwt token from the bearer token
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )
            wallet_token: str = payload.get("key")
            wallet_id: str = payload.get("sub")

            # pass this via starlette context
            context["TENANT_WALLET_TOKEN"] = wallet_token
            context["TENANT_WALLET_ID"] = uuid.UUID(wallet_id)

        response = await call_next(request)
        return response


async def authenticate_tenant(username: str, password: str):
    """Fetch the wallet bearer token (returns None if not found)."""
    wallet_id = username
    wallet_key = password
    body = {"wallet_key": wallet_key}
    try:
        results = await au.acapy_admin_request(
            "POST", f"multitenancy/wallet/{wallet_id}/token", data=body, tenant=False
        )
        jwt_token = results["token"]

        # pass this via starlette context
        context["TENANT_WALLET_TOKEN"] = jwt_token
        context["TENANT_WALLET_ID"] = uuid.UUID(wallet_id)
        tenant = {"wallet_id": wallet_id, "wallet_token": jwt_token}

        return tenant
    except Exception:
        return None
