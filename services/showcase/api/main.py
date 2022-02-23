import logging
import os
import time
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings

from api.endpoints.routes.sandbox import router as sandbox_router
from api.endpoints.routes.webhooks import router as webhooks_router
from api.core.exception_handlers import add_exception_handlers

os.environ["TZ"] = settings.TIMEZONE
time.tzset()

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

origins = [
    "http://localhost",
    "http://localhost:8080",
]

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

if __name__ == "__main__":
    print("main.")
    uvicorn.run(app, host="0.0.0.0", port=5200)
