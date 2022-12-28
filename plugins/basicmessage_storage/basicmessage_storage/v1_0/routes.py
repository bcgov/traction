import functools
import logging
import uuid

from aiohttp import web
from aiohttp_apispec import (
    docs,
    response_schema,
    querystring_schema,
    match_info_schema,
    request_schema,
)
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.util import time_now, str_to_epoch
from aries_cloudagent.multitenant.error import WalletKeyMissingError
from aries_cloudagent.protocols.basicmessage.v1_0.message_types import SPEC_URI
from aries_cloudagent.protocols.basicmessage.v1_0.routes import (
    BasicConnIdMatchInfoSchema,
    SendMessageSchema,
    BasicMessageModuleResponseSchema,
    connections_send_message,
)
from aries_cloudagent.storage.error import StorageError, StorageNotFoundError
from marshmallow import fields, validate

from .models import BasicMessageRecord, BasicMessageRecordSchema

LOGGER = logging.getLogger(__name__)


def error_handler(func):
    @functools.wraps(func)
    async def wrapper(request):
        try:
            ret = await func(request)
            return ret
        except StorageNotFoundError as err:
            raise web.HTTPNotFound(reason=err.roll_up) from err
        except WalletKeyMissingError as err:
            raise web.HTTPUnauthorized(reason=err.roll_up) from err
        except (StorageError, BaseModelError) as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err
        except Exception as err:
            LOGGER.error(err)
            raise err

    return wrapper


class BasicMessageListSchema(OpenAPISchema):
    results = fields.List(
        fields.Nested(BasicMessageRecordSchema()),
        description="List of basic message records",
    )


class BasicMessageListQueryStringSchema(OpenAPISchema):
    connection_id = fields.Str(
        description=(
            "Connection identifier, if none specified, "
            "then return messages from all connections."
        ),
    )
    state = fields.Str(
        description="Message state",
        required=False,
        validate=validate.OneOf(
            [BasicMessageRecord.STATE_SENT, BasicMessageRecord.STATE_RECV]
        ),
    )


@docs(
    tags=["basicmessage"],
    summary="Send a basic message to a connection (basicmessage_storage v1_0 plugin)",
)
@match_info_schema(BasicConnIdMatchInfoSchema())
@request_schema(SendMessageSchema())
@response_schema(BasicMessageModuleResponseSchema(), 200, description="")
@error_handler
async def plugin_connections_send_message(request: web.BaseRequest):
    """
    Request handler for sending a basic message to a connection.

    Args:
        request: aiohttp request object

    """
    connection_id = request.match_info["conn_id"]
    params = await request.json()
    content = params["content"]

    # call the default send message handler
    response = await connections_send_message(request)

    # create a message record to save...
    sent_msg = {
        "connection_id": connection_id,
        "content": content,
        "message_id": str(uuid.uuid4()),
        "sent_time": time_now(),
    }
    msg: BasicMessageRecord = BasicMessageRecord.deserialize(sent_msg)

    # save it
    context: AdminRequestContext = request["context"]
    profile = context.profile
    try:
        async with profile.session() as session:
            await msg.save(session, reason="New sent message")
            LOGGER.debug(msg)
    except Exception as err:
        LOGGER.error(err)
        raise err

    return response


@docs(
    tags=["basicmessage"],
    summary="Query messages from all agents (basicmessage_storage v1_0 plugin)",
)
@querystring_schema(BasicMessageListQueryStringSchema())
@response_schema(BasicMessageListSchema(), 200, description="")
@error_handler
async def all_messages_list(request: web.BaseRequest):
    """
    Request handler for searching basic message records from All agents/connections.

    Args:
        request: aiohttp request object

    Returns:
        The message list response

    """
    context: AdminRequestContext = request["context"]

    tag_filter = {}
    post_filter = {
        k: request.query[k]
        for k in ("connection_id", "state")
        if request.query.get(k, "") != ""
    }
    profile = context.profile
    try:
        async with profile.session() as session:
            records = await BasicMessageRecord.query(
                session=session,
                tag_filter=tag_filter,
                post_filter_positive=post_filter,
                alt=True,
            )
        results = [record.serialize() for record in records]
        # return sorted by most recent first
        results.sort(key=lambda x: str_to_epoch(x["created_at"]), reverse=True)
    except (StorageError, BaseModelError) as err:
        raise web.HTTPBadRequest(reason=err.roll_up) from err

    return web.json_response({"results": results})


async def register(app: web.Application):
    """Register routes."""
    # we want to save messages when sent, so replace the default send message endpoint
    has_send_message = False
    for r in app.router.routes():
        if r.method == "POST":
            if (
                r.resource
                and r.resource.canonical == "/connections/{conn_id}/send-message"
            ):
                LOGGER.info(
                    f"found route: {r.method} {r.resource.canonical} ({r.handler})"
                )
                LOGGER.info(f"... replacing current handler: {r.handler}")
                r._handler = plugin_connections_send_message
                LOGGER.info(f"... with new handler: {r.handler}")
                has_send_message = True

    # ok, just in case we get loaded before the builtin send-message (should be impossible)
    # let's make sure we've added endpoint we expect
    if not has_send_message:
        LOGGER.info(f"adding POST /connections/<conn_id>/send-message route")
        app.add_routes(
            [
                web.post(
                    "/connections/{conn_id}/send-message",
                    plugin_connections_send_message,
                ),
            ]
        )

    # add in the message list(s) route
    app.add_routes([web.get("/basicmessages", all_messages_list, allow_head=False)])


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "basicmessage",
            "description": "Simple messaging",
            "externalDocs": {"description": "Specification", "url": SPEC_URI},
        }
    )
