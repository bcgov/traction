from fastapi import FastAPI
from api.resources.tenant import router as tenant_router
from api.db import init_db

from api.models import tenant

app = FastAPI()

app.include_router(tenant_router, prefix="/tenant")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
async def hello_world():
    return {"hello": "world"}
