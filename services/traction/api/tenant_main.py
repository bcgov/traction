import logging

from fastapi import APIRouter, Depends, FastAPI
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from api.endpoints.dependencies.db import get_db

from api.core.config import settings
from api.endpoints.routes.tenant_api import tenant_router
from api.endpoints.dependencies.jwt_security import AccessToken
from api.endpoints.dependencies.tenant_security import (
    JWTTFetchingMiddleware,
    get_tenant_access_token,
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
        prefix=settings.API_V0_STR,
        dependencies=[Depends(OAuth2PasswordBearer(tokenUrl="token"))],
    )
    return application


@router.post("/token", response_model=AccessToken)
async def login_for_tenant_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    access_token = await get_tenant_access_token(form_data, db)
    return access_token
