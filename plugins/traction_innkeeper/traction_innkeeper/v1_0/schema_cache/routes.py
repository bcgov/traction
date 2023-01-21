import functools
import logging

from aiohttp import web
from aiohttp_apispec import docs, response_schema, match_info_schema, request_schema
from aries_cloudagent.admin.request_context import AdminRequestContext

from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema

from aries_cloudagent.storage.error import StorageNotFoundError, StorageError
from marshmallow import fields

from .models import SchemaCacheRecordSchema
from .schema_cache_service import (
    list_schemas_from_cache,
    get_schema_from_cache,
    add_schema_to_cache,
)

LOGGER = logging.getLogger(__name__)

SWAGGER_SCHEMA_CACHE = "schema-cache"


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


class SchemaCacheListSchema(OpenAPISchema):
    """Response schema for schema cache list."""

    results = fields.List(
        fields.Nested(SchemaCacheRecordSchema()),
        description="List of schema cache records",
    )


class SchemaIdMatchInfoSchema(OpenAPISchema):
    schema_id = fields.Str(description="Schema identifier", required=True)


class SchemaCacheAddSchema(OpenAPISchema):
    schema_id = fields.Str(description="Schema identifier", required=True)


@docs(
    tags=[SWAGGER_SCHEMA_CACHE],
)
@response_schema(SchemaCacheListSchema(), 200, description="")
@error_handler
async def schema_cache_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile

    tag_filter = {}
    post_filter = {}
    records = await list_schemas_from_cache(profile, tag_filter, post_filter)
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


@docs(
    tags=[SWAGGER_SCHEMA_CACHE],
)
@request_schema(SchemaCacheAddSchema())
@response_schema(SchemaCacheRecordSchema(), 200, description="")
@error_handler
async def schema_cache_add(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    body = await request.json()

    record = await add_schema_to_cache(profile, body["schema_id"])

    return web.json_response(record.serialize())


@docs(
    tags=[SWAGGER_SCHEMA_CACHE],
)
@match_info_schema(SchemaIdMatchInfoSchema())
@response_schema(SchemaCacheRecordSchema(), 200, description="")
@error_handler
async def schema_cache_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile
    schema_id = request.match_info["schema_id"]

    record = await get_schema_from_cache(profile, schema_id)

    return web.json_response(record.serialize())


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    app.add_routes(
        [
            web.get(
                f"/schema-cache",
                schema_cache_list,
                allow_head=False,
            ),
            web.post("/schema-cache", schema_cache_add),
            web.get(
                "/schema-cache/{schema_id}",
                schema_cache_get,
                allow_head=False,
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
            "name": SWAGGER_SCHEMA_CACHE,
            "description": "Traction Schema Cache - ledger schema cache (traction_innkeeper/schema_cache v1_0 plugin)",
        }
    )
