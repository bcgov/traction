import os
import time

import uvicorn
from fastapi import FastAPI

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


app = get_application()
app.include_router(sandbox_router, tags=["sandbox"])
app.include_router(webhooks_router, tags=["webhooks"])


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    print("main.")
    uvicorn.run(app, host="0.0.0.0", port=5200)
