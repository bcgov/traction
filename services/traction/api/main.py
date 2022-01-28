import os
import time
from datetime import timedelta

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware import Middleware
from starlette.responses import JSONResponse
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from api.db.errors import DoesNotExist, AlreadyExists
from api.endpoints.routes.api import api_router
from api.endpoints.routes.webhooks import router as webhook_router
from api.tenant_security import (
    TenantToken,
    authenticate_tenant,
    create_access_token,
    JWTTFetchingMiddleware,
)
from api.core.config import settings


os.environ["TZ"] = settings.TIMEZONE
time.tzset()

middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    ),
    Middleware(JWTTFetchingMiddleware),
]


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        middleware=middleware,
    )
    application.include_router(api_router, prefix=settings.API_V1_STR)
    application.include_router(webhook_router, prefix="/webhook")
    return application


app = get_application()


@app.exception_handler(DoesNotExist)
async def does_not_exist_exception_handler(request: Request, exc: DoesNotExist):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )


@app.exception_handler(AlreadyExists)
async def already_exists_exception_handler(request: Request, exc: AlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": str(exc)},
    )


@app.get("/", tags=["liveness"])
def main():
    return {"status": "ok"}


@app.post("/token", response_model=TenantToken)
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


if __name__ == "__main__":
    print("main.....")
    uvicorn.run(app, host="0.0.0.0", port=8080)
