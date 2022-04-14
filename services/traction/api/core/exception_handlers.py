# Exception handlers
from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from api.db.errors import AlreadyExists, DoesNotExist
from api.endpoints.models.v1.errors import MethodNotImplementedError


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

    @_app.exception_handler(NotImplementedError)
    async def not_implemented_exception_handler(
        request: Request, exc: NotImplementedError
    ):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"message": str(exc)},
        )

    @_app.exception_handler(MethodNotImplementedError)
    async def method_not_implemented_exception_handler(
        request: Request, exc: MethodNotImplementedError
    ):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return JSONResponse(
            status_code=status_code,
            content={
                "request_id": context.data[HeaderKeys.request_id],
                "status": status_code,
                "code": exc.code,
                "title": exc.title,
                "detail": exc.detail,
                "links": exc.links,
            },
        )
