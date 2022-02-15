# Exception handlers
from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.db.errors import AlreadyExists, DoesNotExist


def add_exception_handlers(_app: FastAPI):
    @_app.exception_handler(DoesNotExist)
    async def does_not_exist_exception_handler(request: Request, exc: DoesNotExist):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": str(exc)},
        )

    @_app.exception_handler(AlreadyExists)
    async def already_exists_exception_handler(request: Request, exc: AlreadyExists):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(exc)},
        )
