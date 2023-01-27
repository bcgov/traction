import functools
import logging

from aiohttp import web
from aiohttp_apispec import docs, response_schema, match_info_schema
from aries_cloudagent.admin.request_context import AdminRequestContext

from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema

from aries_cloudagent.storage.error import StorageNotFoundError, StorageError
from marshmallow import fields

from .models import CredDefStorageRecordSchema
from .creddef_storage_service import CredDefStorageService

LOGGER = logging.getLogger(__name__)

SWAGGER_CATEGORY = "credential-definition-storage"


def error_handler(func):
    @functools.wraps(func)
    async def wrapper(request):
        try:
            ret = await func(request)
            return ret
        except StorageNotFoundError as err:
            raise web.HTTPNotFound(reason=err.roll_up) from err
        except (StorageError, BaseModelError) as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err
        except Exception as err:
            LOGGER.error(err)
            raise err

    return wrapper


class CredDefStorageListSchema(OpenAPISchema):
    """Response schema for schema storage list."""

    results = fields.List(
        fields.Nested(CredDefStorageRecordSchema()),
        description="List of cred def storage records",
    )


class CredDefIdMatchInfoSchema(OpenAPISchema):
    cred_def_id = fields.Str(
        description="Credential Definition identifier", required=True
    )


class OperationResponseSchema(OpenAPISchema):
    """Response schema for simple operations."""

    success = fields.Bool(
        required=True,
        description="True if operation successful, false if otherwise",
    )


@docs(
    tags=[SWAGGER_CATEGORY],
)
@response_schema(CredDefStorageListSchema(), 200, description="")
@error_handler
async def creddef_storage_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    storage_srv = context.inject_or(CredDefStorageService)

    tag_filter = {}
    post_filter = {}
    records = await storage_srv.list_items(profile, tag_filter, post_filter)
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(CredDefIdMatchInfoSchema())
@response_schema(CredDefStorageRecordSchema(), 200, description="")
@error_handler
async def creddef_storage_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    storage_srv = context.inject_or(CredDefStorageService)
    cred_def_id = request.match_info["cred_def_id"]

    record = await storage_srv.read_item(profile, cred_def_id)

    return web.json_response(record.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(CredDefIdMatchInfoSchema())
@response_schema(OperationResponseSchema(), 200, description="")
@error_handler
async def creddef_storage_remove(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    storage_srv = context.inject_or(CredDefStorageService)
    cred_def_id = request.match_info["cred_def_id"]

    success = await storage_srv.remove_item(profile, cred_def_id)

    return web.json_response({"success": success})


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    app.add_routes(
        [
            web.get(
                "/credential-definition-storage",
                creddef_storage_list,
                allow_head=False,
            ),
            web.get(
                "/credential-definition-storage/{cred_def_id}",
                creddef_storage_get,
                allow_head=False,
            ),
            web.delete(
                "/credential-definition-storage/{cred_def_id}",
                creddef_storage_remove,
            ),
        ]
    )
    LOGGER.info("< registering routes")


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []

    app._state["swagger_dict"]["tags"].append(
        {
            "name": SWAGGER_CATEGORY,
            "description": "Traction Credential Definition Storage - Local storage of credential definition metadata (traction_innkeeper/creddef_storage v1_0 plugin)",
        }
    )
