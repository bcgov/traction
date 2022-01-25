from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_context import context, plugins
from starlette_context.middleware import RawContextMiddleware

from api.resources.ledger import router as ledger_router
from api.resources.tenant import router as tenant_router

from api.models import tenant  # noqa F401


middleware = [
    Middleware(
        RawContextMiddleware,
        plugins=(
            plugins.RequestIdPlugin(),
            plugins.CorrelationIdPlugin()
        )
    )
]

app = FastAPI(middleware=middleware)

app.include_router(ledger_router, prefix="/ledger")
app.include_router(tenant_router, prefix="/tenant")


@app.get("/")
async def hello_world():
    return {"hello": "world"}
