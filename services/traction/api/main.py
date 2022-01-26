from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware import Middleware
from starlette_context import plugins
from starlette_context.middleware import RawContextMiddleware

from api.resources.connections import router as connections_router
from api.resources.ledger import router as ledger_router
from api.resources.tenant import router as tenant_router
from api.tenant_security import (
    TenantToken,
    authenticate_tenant,
    create_access_token,
    JWTTFetchingMiddleware,
)
from config import Config


middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(plugins.RequestIdPlugin(), plugins.CorrelationIdPlugin()),
    ),
    Middleware(JWTTFetchingMiddleware),
]

app = FastAPI(middleware=middleware)

app.include_router(connections_router, prefix="/connections")
app.include_router(ledger_router, prefix="/ledger")
app.include_router(tenant_router, prefix="/tenant")


@app.get("/")
async def hello_world():
    return {"hello": "world"}


@app.post("/token", response_model=TenantToken)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    tenant = await authenticate_tenant(form_data.username, form_data.password)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect wallet_id or wallet_key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": tenant["wallet_id"], "key": tenant["wallet_token"]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
