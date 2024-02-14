import sys

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

from . import utils


state = {"tenant": None}


@asynccontextmanager
async def before_startup(app: FastAPI):
    """Create a new tenant before starting up the app."""

    try:
        tenant = await utils.create_tenant("tenant_name")
        state["tenant"] = tenant
        yield
    except:
        sys.exit(1)


app = FastAPI(lifespan=before_startup)


@app.get("/tenant")
async def get_tenant():
    """Get the wallet id and token for the tenant."""

    try:
        if not (token := state["tenant"]["token"]) or not (
            tenant_name := state["tenant"]["tenant_name"]
        ):
            raise HTTPException(
                status_code=404, detail="Token or tenant name not found"
            )

        return {"tenant": tenant_name, "token": token}
    except:
        raise HTTPException(status_code=500, detail="Server error")


@app.get("/invitation")
async def get_invitation(request: Request):
    """Get the invitation for the tenant. Token must be in the header."""

    try:
        if not (token := request.headers.get("authorization").replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Token not found")

        headers = utils.get_tenant_auth_headers(token)
        return await utils.create_invitation(headers)
    except:
        raise HTTPException(status_code=500, detail="Server error")


@app.post("/connection")
async def create_connection(request: Request):
    """Create a connection for the tenant.

    Token must be in the header. Invitation must be in the body.
    """

    try:
        if not (token := request.headers.get("authorization").replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Token not found")

        if not (invitation := await request.json()):
            raise HTTPException(status_code=400, detail="Invitation is required")

        headers = utils.get_tenant_auth_headers(token)
        return await utils.create_connection(headers, invitation)
    except:
        raise HTTPException(status_code=500, detail="Server error")
