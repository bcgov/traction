from datetime import timedelta

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from api.endpoints.routes.tenant_api import tenant_router
from api.tenant_security import (
    TenantToken,
    authenticate_tenant,
    create_access_token,
    JWTTFetchingMiddleware,
)
from api.core.config import settings


middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    ),
    Middleware(JWTTFetchingMiddleware),
]

router = APIRouter()


def get_tenantapp() -> FastAPI:
    application = FastAPI(
        title=settings.TENANT_TITLE,
        description=settings.TENANT_DESCRIPTION,
        debug=settings.DEBUG,
        middleware=middleware,
    )
    application.include_router(tenant_router, prefix=settings.API_V1_STR)
    application.include_router(router, prefix="")
    return application


@router.post("/token", response_model=TenantToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    tenant = await authenticate_tenant(form_data.username, form_data.password)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect wallet_id or wallet_key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": tenant["wallet_id"], "key": tenant["wallet_token"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
