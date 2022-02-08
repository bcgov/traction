from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from api.endpoints.routes.endorser import router as endorser_router
from api.endpoints.dependencies.jwt_security import AccessToken, create_access_token
from api.core.config import settings as s


middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    ),
]

router = APIRouter()


def get_endorserapp() -> FastAPI:
    application = FastAPI(
        title=s.TITLE,
        description=s.DESCRIPTION,
        debug=s.DEBUG,
        middleware=middleware,
    )
    # mount the token endpoint
    application.include_router(router, prefix="")
    # mount other endpoints, these will be secured by the above token endpoint
    application.include_router(
        endorser_router,
        prefix=s.API_V1_STR,
        dependencies=[Depends(OAuth2PasswordBearer(tokenUrl="token"))],
        tags=["endorser"],
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
            detail="Incorrect Endorser Api Admin User or Endorser Api Admin Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_access_token(data={"sub": form_data.username})


async def authenticate_innkeeper(username: str, password: str):
    if s.ENDORSER_API_ADMIN_USER == username and s.ENDORSER_API_ADMIN_KEY == password:
        return True
    return False
