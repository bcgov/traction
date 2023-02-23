import functools
import logging

from aiohttp import web
from aiohttp_apispec import docs, match_info_schema, response_schema, request_schema
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.connections.models.conn_record import ConnRecord, ConnRecordSchema
from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.protocols.connections.v1_0.routes import (
    ConnectionsConnIdMatchInfoSchema,
)
from aries_cloudagent.storage.error import StorageNotFoundError, StorageError
from marshmallow import fields

LOGGER = logging.getLogger(__name__)


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


class UpdateConnectionRequestSchema(OpenAPISchema):
    """Request schema for updating a connection."""

    alias = fields.Str(
        required=False,
        description="Optional alias to apply to connection for later use",
        example="Bob, providing quotes",
    )


@docs(
    tags=["connection"],
    summary="Update connection (connection_update v1_0 plugin)",
    description="Currently, only `alias` can be updated.",
)
@match_info_schema(ConnectionsConnIdMatchInfoSchema())
@request_schema(UpdateConnectionRequestSchema)
@response_schema(ConnRecordSchema(), 200, description="")
@error_handler
async def connections_update(request: web.BaseRequest):
    """Update data for a connection record."""
    context: AdminRequestContext = request["context"]
    connection_id = request.match_info["conn_id"]

    body = await request.json()
    alias = body.get("alias")

    profile = context.profile

    async with profile.session() as session:
        record = await ConnRecord.retrieve_by_id(
            session, connection_id, for_update=True
        )
        if alias:
            record.alias = alias
        await record.save(session, reason="Update connection alias")
        result = record.serialize()

    return web.json_response(result)


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> register routes")
    app.add_routes(
        [
            web.put(
                "/connections/{conn_id}",
                connections_update,
            ),
        ]
    )
    LOGGER.info("< register routes")


def post_process_routes(app: web.Application):
    LOGGER.info("> post-process routes")
    LOGGER.info("< post-process routes")
