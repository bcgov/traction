import logging
import os
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocket, WebSocketDisconnect

from api.core.config import settings

from api.endpoints.routes.sandbox import router as sandbox_router
from api.endpoints.routes.webhooks import router as webhooks_router
from api.core.exception_handlers import add_exception_handlers
from api.services.websockets import notifier

os.environ["TZ"] = settings.TIMEZONE
time.tzset()

# setup loggers
logging_file_path = (Path(__file__).parent / "logging.conf").resolve()
logging.config.fileConfig(logging_file_path, disable_existing_loggers=False)

logger = logging.getLogger(__name__)


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        middleware=None,
    )
    return application


def get_api() -> FastAPI:
    api = FastAPI(
        title=settings.TITLE,
        description=settings.DESCRIPTION,
        debug=settings.DEBUG,
        middleware=None,
    )
    # mount api routers here...
    api.include_router(sandbox_router, prefix=settings.API_V1_STR, tags=["sandbox"])
    api.include_router(webhooks_router, prefix=settings.API_V1_STR, tags=["webhooks"])
    return api


app = get_application()
api = get_api()
app.mount("/api", api)


# frontend websockets
# make sure this is before the static files and cors origins.
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await notifier.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")
    except WebSocketDisconnect:
        notifier.remove(websocket)


# Frontend Serving

origins = settings.SHOWCASE_CORS_URLS.split(",")

if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            response = await super().get_response(".", scope)
        return response


static_files = Path(settings.SHOWCASE_STATIC_FILES).resolve()

app.mount(
    "/",
    SPAStaticFiles(directory=static_files, html=True, check_dir=True),
    name="dist",
)

add_exception_handlers(app)
add_exception_handlers(api)


@app.on_event("startup")
async def startup():
    logger.debug("@app.on_event(startup)")
    # Prime the push notification generator
    await notifier.generator.asend(None)


if __name__ == "__main__":
    print("main.")
    uvicorn.run(app, host="0.0.0.0", port=5200)
