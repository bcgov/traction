# Exception handlers
from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from api.db.errors import AlreadyExists, DoesNotExist
from api.endpoints.models.v1.errors import (
    MethodNotImplementedError,
    BaseError,
    AlreadyExistsError,
    NotFoundError,
    IdNotMatchError,
    NotAnIssuerError,
)


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

    @_app.exception_handler(AlreadyExistsError)
    async def resource_already_exists_exception_handler(
        request: Request, exc: AlreadyExistsError
    ):
        status_code = status.HTTP_409_CONFLICT
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

    @_app.exception_handler(NotFoundError)
    async def resource_not_found_implemented_exception_handler(
        request: Request, exc: NotFoundError
    ):
        status_code = status.HTTP_404_NOT_FOUND
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

    @_app.exception_handler(IdNotMatchError)
    async def id_not_match_exception_handler(request: Request, exc: IdNotMatchError):
        status_code = status.HTTP_409_CONFLICT
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

    @_app.exception_handler(NotAnIssuerError)
    async def not_an_issuer_exception_handler(request: Request, exc: NotAnIssuerError):
        status_code = status.HTTP_401_UNAUTHORIZED
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

    @_app.exception_handler(BaseError)
    async def base_error_exception_handler(request: Request, exc: BaseError):
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
