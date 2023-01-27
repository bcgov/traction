import functools
import logging

from aiohttp import web
from aiohttp_apispec import docs, response_schema, match_info_schema, request_schema
from aries_cloudagent.admin.request_context import AdminRequestContext

from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema

from aries_cloudagent.storage.error import StorageNotFoundError, StorageError
from marshmallow import fields

from .models import SchemaStorageRecordSchema
from .schema_storage_service import SchemaStorageService

LOGGER = logging.getLogger(__name__)

SWAGGER_CATEGORY = "schema-storage"


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


class SchemaStorageListSchema(OpenAPISchema):
    """Response schema for schema storage list."""

    results = fields.List(
        fields.Nested(SchemaStorageRecordSchema()),
        description="List of schema storage records",
    )


class SchemaIdMatchInfoSchema(OpenAPISchema):
    schema_id = fields.Str(description="Schema identifier", required=True)


class SchemaStorageAddSchema(OpenAPISchema):
    schema_id = fields.Str(description="Schema identifier", required=True)


class OperationResponseSchema(OpenAPISchema):
    """Response schema for simple operations."""

    success = fields.Bool(
        required=True,
        description="True if operation successful, false if otherwise",
    )


@docs(
    tags=[SWAGGER_CATEGORY],
)
@response_schema(SchemaStorageListSchema(), 200, description="")
@error_handler
async def schema_storage_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    storage_srv = context.inject_or(SchemaStorageService)

    tag_filter = {}
    post_filter = {}
    records = await storage_srv.list_items(profile, tag_filter, post_filter)
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@request_schema(SchemaStorageAddSchema())
@response_schema(SchemaStorageRecordSchema(), 200, description="")
@error_handler
async def schema_storage_add(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    storage_srv = context.inject_or(SchemaStorageService)
    body = await request.json()

    record = await storage_srv.add_item(profile, body["schema_id"])

    return web.json_response(record.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(SchemaIdMatchInfoSchema())
@response_schema(SchemaStorageRecordSchema(), 200, description="")
@error_handler
async def schema_storage_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    storage_srv = context.inject_or(SchemaStorageService)
    schema_id = request.match_info["schema_id"]

    record = await storage_srv.read_item(profile, schema_id)

    return web.json_response(record.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(SchemaIdMatchInfoSchema())
@response_schema(OperationResponseSchema(), 200, description="")
@error_handler
async def schema_storage_remove(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    storage_srv = context.inject_or(SchemaStorageService)
    schema_id = request.match_info["schema_id"]

    success = await storage_srv.remove_item(profile, schema_id)

    return web.json_response({"success": success})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@response_schema(SchemaStorageListSchema(), 200, description="")
@error_handler
async def schema_storage_sync_created(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    storage_srv = context.inject_or(SchemaStorageService)

    records = await storage_srv.sync_created(profile)
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    app.add_routes(
        [
            web.get(
                "/schema-storage",
                schema_storage_list,
                allow_head=False,
            ),
            web.post("/schema-storage", schema_storage_add),
            web.get(
                "/schema-storage/{schema_id}",
                schema_storage_get,
                allow_head=False,
            ),
            web.delete(
                "/schema-storage/{schema_id}",
                schema_storage_remove,
            ),
            web.post("/schema-storage/sync-created", schema_storage_sync_created),
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
            "description": "Traction Schema Storage - Local storage of schema metadata (traction_innkeeper/schema_storage v1_0 plugin)",
        }
    )
