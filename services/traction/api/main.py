from fastapi import FastAPI
from api.resources.tenant import router as tenant_router

from api.models import tenant  # noqa F401

app = FastAPI()

app.include_router(tenant_router, prefix="/tenant")


@app.get("/")
async def hello_world():
    return {"hello": "world"}
