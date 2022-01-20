from fastapi import FastAPI
from api.resources import tenant

app = FastAPI()

app.include_router(tenant.router, prefix="/tenant")

@app.get("/")
async def hello_world():
    return {"hello": "world"}
