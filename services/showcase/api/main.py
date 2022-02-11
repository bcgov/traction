import os
import time

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.core.config import settings

from api.endpoints.routes.sandbox import router as sandbox_router
from api.endpoints.routes.webhooks import router as webhooks_router

os.environ["TZ"] = settings.TIMEZONE
time.tzset()


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
app.mount("/api", get_api())

# Frontend Serving

class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 404:
            response = await super().get_response('.', scope)
        return response

app.mount('/', SPAStaticFiles(directory='frontend/dist', html=True), name='dist')

if __name__ == "__main__":
    print("main.")
    uvicorn.run(app, host="0.0.0.0", port=5200)
