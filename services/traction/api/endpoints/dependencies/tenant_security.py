import logging
import uuid

from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette_context import context
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from acapy_client.api.multitenancy_api import MultitenancyApi
from acapy_client.model.create_wallet_token_request import CreateWalletTokenRequest

from api.api_client_utils import get_api_client

from api.core.config import settings
from api.db.errors import DoesNotExist
from api.db.repositories.tenants import TenantsRepository
from api.endpoints.dependencies.jwt_security import create_access_token

logger = logging.getLogger(__name__)

# TODO not sure if these should be global or per-request
multitenancy_api = MultitenancyApi(api_client=get_api_client())


def get_from_context(name: str):
    result = context.get(name)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Error not authenticated",
        )
    return result


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
            tenant_id: str = payload.get("t_id")

            # pass this via starlette context
            context["TENANT_WALLET_TOKEN"] = wallet_token
            context["TENANT_WALLET_ID"] = uuid.UUID(wallet_id)
            context["TENANT_ID"] = uuid.UUID(tenant_id)

        response = await call_next(request)
        return response


async def authenticate_tenant(username: str, password: str, db: AsyncSession):
    """Fetch the wallet bearer token (returns None if not found)."""
    wallet_id = username
    wallet_key = password
    data = {"wallet_key": wallet_key}
    try:
        token_request = CreateWalletTokenRequest(**data)
        token_response = multitenancy_api.multitenancy_wallet_wallet_id_token_post(
            wallet_id, **{"body": token_request}
        )
        jwt_token = token_response.token
        try:
            # fetch the tenant, we can confirm the id is valid in traction too...
            tenant_repo = TenantsRepository(db)
            tnt = await tenant_repo.get_by_wallet_id(uuid.UUID(wallet_id))
            # TODO: should we check if tenant is active?

            # pass this via starlette context
            context["TENANT_WALLET_TOKEN"] = jwt_token
            context["TENANT_WALLET_ID"] = uuid.UUID(wallet_id)
            context["TENANT_ID"] = tnt.id
            tenant = {
                "tenant_id": str(tnt.id),
                "wallet_id": wallet_id,
                "wallet_token": jwt_token,
            }

            return tenant
        except DoesNotExist:
            return None

    except Exception:
        return None


async def get_tenant_access_token(
    form_data: OAuth2PasswordRequestForm, db: AsyncSession
):
    tenant = await authenticate_tenant(form_data.username, form_data.password, db)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect wallet_id or wallet_key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token(
        data={
            "sub": tenant["wallet_id"],
            "key": tenant["wallet_token"],
            "t_id": tenant["tenant_id"],
        }
    )
