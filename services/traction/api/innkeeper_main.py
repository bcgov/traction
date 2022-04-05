from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from api.endpoints.routes.innkeeper import router as innkeeper_router
from api.endpoints.dependencies.jwt_security import AccessToken, create_access_token
from api.core.config import settings as s


middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    ),
]

router = APIRouter()


def get_innkeeperapp() -> FastAPI:
    application = FastAPI(
        title=s.INNKEEPER_TITLE,
        description=s.INNKEEPER_DESCRIPTION,
        debug=s.DEBUG,
        middleware=middleware,
    )
    # mount the token endpoint
    application.include_router(router, prefix="")
    # mount other endpoints, these will be secured by the above token endpoint
    application.include_router(
        innkeeper_router,
        prefix=s.API_V0_STR,
        dependencies=[Depends(OAuth2PasswordBearer(tokenUrl="token"))],
        tags=["innkeeper"],
    )
    return application


@router.post("/token", response_model=AccessToken)
async def login_for_traction_api_admin(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    authenticated = await authenticate_innkeeper(form_data.username, form_data.password)
    if not authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect Traction Api Admin User or Traction Api Admin Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token(data={"sub": form_data.username})


async def authenticate_innkeeper(username: str, password: str):
    if s.TRACTION_API_ADMIN_USER == username and s.TRACTION_API_ADMIN_KEY == password:
        return True
    return False
