from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette_context import context, plugins
from starlette_context.middleware import RawContextMiddleware

from api.resources.ledger import router as ledger_router
from api.resources.tenant import router as tenant_router

from api.models import tenant  # noqa F401
from api import acapy_utils as au



class JWTTFetchingMiddleware(BaseHTTPMiddleware):
    """Middleware to inject tenant JWT into context."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # TODO wallet_id and key should be in the request headers, just fake it for now
        # grab a tenant jwt if there is one available
        results = await au.acapy_admin_request("GET", "multitenancy/wallets", tenant=False)
        wallets = results["results"]
        if len(wallets) > 0:
            # get the tenant's JWT token
            wallet_id = wallets[0]["wallet_id"]
            # hack - assume wallet_name and wallet_key are the same value
            wallet_key = wallets[0]["settings"]["wallet.name"]
            body = {"wallet_key": wallet_key}
            results = await au.acapy_admin_request("POST", f"multitenancy/wallet/{wallet_id}/token", data=body, tenant=False)
            jwt_token = results["token"]

            # pass this via starlette context
            context["TENANT_WALLET_TOKEN"] = jwt_token

        response = await call_next(request)
        return response


middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin()
        ),
    ),
    Middleware(JWTTFetchingMiddleware),
]

app = FastAPI(middleware=middleware)

app.include_router(ledger_router, prefix="/ledger")
app.include_router(tenant_router, prefix="/tenant")


@app.get("/")
async def hello_world():
    return {"hello": "world"}
