import os
import time

import uvicorn
from fastapi import FastAPI, Request
from starlette import status
from starlette.responses import JSONResponse

from api.db.errors import DoesNotExist, AlreadyExists
from api.endpoints.routes.api import api_router
from api.core.config import settings

os.environ["TZ"] = settings.TIMEZONE
time.tzset()


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.TITLE, description=settings.DESCRIPTION, debug=settings.DEBUG
    )
    application.include_router(api_router, prefix=settings.API_V1_STR)
    return application


app = get_application()


@app.exception_handler(DoesNotExist)
async def does_not_exist_exception_handler(request: Request, exc: DoesNotExist):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"message": str(exc)},
    )


@app.exception_handler(AlreadyExists)
async def already_exists_exception_handler(request: Request, exc: AlreadyExists):
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={"message": str(exc)},
    )


@app.get("/", tags=["liveness"])
def main():
    return {"status": "ok"}


if __name__ == "__main__":
    print("main.....")
    uvicorn.run(app, host="0.0.0.0", port=8080)
