import logging

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware
from api.endpoints.dependencies.oauth_wrapper import check_oauth

from api.core.config import settings
from api.endpoints.routes.tenant_api import tenant_router
from api.endpoints.dependencies.jwt_security import AccessToken, create_access_token
from api.endpoints.dependencies.tenant_security import (
    JWTTFetchingMiddleware,
    authenticate_tenant,
)


logger = logging.getLogger(__name__)

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
    # mount the token endpoint
    application.include_router(router, prefix="")
    # mount other endpoints, these will be secured by the above token endpoint
    application.include_router(
        tenant_router,
        prefix=settings.API_V1_STR,
        dependencies=[Depends(check_oauth(tokenUrl="token"))],
    )
    return application


@router.post("/token", response_model=AccessToken)
async def login_for_tenant_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    tenant = await authenticate_tenant(form_data.username, form_data.password)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect wallet_id or wallet_key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token(
        data={"sub": tenant["wallet_id"], "key": tenant["wallet_token"]}
    )
