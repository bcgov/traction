from datetime import datetime, timedelta
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel
from starlette_context import context
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import Response

from api import acapy_utils as au
from api.core.config import settings


class TenantToken(BaseModel):
    access_token: str
    token_type: str


class TenantTokenData(BaseModel):
    wallet_id: Optional[str] = None
    bearer_token: Optional[str] = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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

            # pass this via starlette context
            context["TENANT_WALLET_TOKEN"] = wallet_token

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
        tenant = {"wallet_id": wallet_id, "wallet_token": jwt_token}

        return tenant
    except Exception:
        return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt
