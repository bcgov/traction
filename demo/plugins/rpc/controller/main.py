import json, sys

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, WebSocket

from . import utils


state = {"tenant": None}


class ConnectionManager:
    """Manage the websocket connections for the tenant."""

    def __init__(self):
        self.connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    async def send(self, message: any, websocket: WebSocket):
        await websocket.send_text(message)

    async def disconnect(self, websocket: WebSocket):
        self.connections.remove(websocket)

    def websocket_by_wallet_id(self, wallet_id: str):
        return next(
            (
                websocket
                for websocket in self.connections
                if websocket.path_params["wallet_id"] == wallet_id
            ),
            None,
        )


@asynccontextmanager
async def before_startup(app: FastAPI):
    """Create a new tenant before starting up the app."""

    try:
        tenant = await utils.create_tenant(f"{utils.r.random_word().capitalize()}")
        state["tenant"] = tenant
        yield
    except:
        sys.exit(1)


app = FastAPI(lifespan=before_startup)
manager = ConnectionManager()


@app.get("/tenant")
async def get_tenant():
    """Get the wallet id and token for the tenant."""

    try:
        if (
            not (token := state["tenant"]["token"])
            or not (tenant_name := state["tenant"]["tenant_name"])
            or not (wallet_id := state["tenant"]["wallet_id"])
        ):
            raise HTTPException(
                status_code=404, detail="Token or tenant name or wallet id not found"
            )

        return {"tenant_name": tenant_name, "token": token, "wallet_id": wallet_id}
    except HTTPException as exc:
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="Server error")


@app.get("/invitation")
async def get_invitation(request: Request):
    """Get the invitation for the tenant. Token must be in the header."""

    try:
        if not (token := request.headers.get("authorization").replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Token not found")

        headers = utils.get_tenant_auth_headers(token)
        return await utils.create_invitation(headers)
    except HTTPException as exc:
        if exc:
            raise exc
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
    except HTTPException as exc:
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="Server error")


@app.post("/drpc/request")
async def send_drpc_request(request: Request):
    """Send a request to the agent for the tenant."""
    try:
        if not (token := request.headers.get("authorization").replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Token not found")

        body = await request.json()

        if not (
            (connection_id := body.get("connection_id"))
            and (rpc_request := body.get("rpc_request"))
        ):
            raise HTTPException(
                status_code=400, detail="Connection id and rpc request is required"
            )
        headers = utils.get_tenant_auth_headers(token)
        return await utils.send_drpc_request(headers, connection_id, rpc_request)
    except HTTPException as exc:
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="Server error")


@app.post("/drpc/response")
async def send_drpc_response(request: Request):
    """Send a response to the agent for the tenant."""
    try:
        if not (token := request.headers.get("authorization").replace("Bearer ", "")):
            raise HTTPException(status_code=401, detail="Token not found")

        body = await request.json()

        if (
            not (connection_id := body.get("connection_id"))
            or not (rpc_request_id := body.get("rpc_request_id"))
            or ((rpc_response := body.get("rpc_response")) == None)
        ):
            raise HTTPException(
                status_code=400,
                detail="Connection id, rpc request id and rpc response is required",
            )
        headers = utils.get_tenant_auth_headers(token)
        return await utils.send_drpc_response(
            headers, connection_id, rpc_request_id, rpc_response
        )
    except HTTPException as exc:
        if exc:
            raise exc
        raise HTTPException(status_code=500, detail="Server error")


@app.post("/webhook/topic/{topic}")
async def recieve_webhook(topic: str, request: Request):
    """Recieve a webhook for the tenant."""
    try:
        message = None
        if topic in ("connections", "drpc_request", "drpc_response"):
            message = await request.json()

        if wallet_id := state["tenant"]["wallet_id"]:
            websocket = manager.websocket_by_wallet_id(wallet_id)

        if websocket and message:
            await manager.send(
                json.dumps({"topic": topic, "message": message}), websocket
            )
    except Exception as exc:
        print(exc)
        raise HTTPException(status_code=500, detail="Server error")


@app.websocket("/ws/{wallet_id}")
async def websocket_endpoint(websocket: WebSocket):
    """Handle the websocket connection for the tenant."""

    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive()
    except:
        await manager.disconnect(websocket)
