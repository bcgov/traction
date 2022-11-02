import logging
import uuid

from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema, match_info_schema, querystring_schema
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.util import time_now
from aries_cloudagent.protocols.basicmessage.v1_0.message_types import SPEC_URI
from aries_cloudagent.protocols.basicmessage.v1_0.routes import BasicMessageModuleResponseSchema, SendMessageSchema, \
    BasicConnIdMatchInfoSchema, connections_send_message
from aries_cloudagent.storage.error import StorageError
from marshmallow import fields, validate

from .models import BasicMessageRecord, BasicMessageRecordSchema

LOGGER = logging.getLogger(__name__)


class BasicMessageListSchema(OpenAPISchema):
    results = fields.List(
        fields.Nested(BasicMessageRecordSchema()),
        description="List of basic message records",
    )


class BasicMessageListQueryStringSchema(OpenAPISchema):
    state = fields.Str(
        description="Message state",
        required=False,
        validate=validate.OneOf(
            [BasicMessageRecord.STATE_SENT, BasicMessageRecord.STATE_RECV]
        ),
    )


def messages_sort_key(rec):
    """Get the sorting key for a basic messages."""
    if rec["state"] == BasicMessageRecord.STATE_SENT:
        pfx = "2"
    elif rec["state"] == BasicMessageRecord.STATE_RECV:
        pfx = "1"
    else:  # GRANTED
        pfx = "0"
    return pfx + rec["created_at"]


@docs(tags=["basicmessage"], summary="Send a basic message to a connection")
@match_info_schema(BasicConnIdMatchInfoSchema())
@request_schema(SendMessageSchema())
@response_schema(BasicMessageModuleResponseSchema(), 200, description="")
async def v0_1_connections_send_message(request: web.BaseRequest):
    # LOGGER.info("> v0_1_connections_send_message")

    # need this for storing our sent message
    connection_id = request.match_info["conn_id"]
    params = await request.json()
    content = params["content"]

    # call the default implementation for send
    response = await connections_send_message(request)

    # there isn't any data in a basic messages response body
    # body = json.loads(response.body)

    # build up our basic message sent record
    sent_msg = {
        'connection_id': connection_id,
        'content': content,
        'message_id': str(uuid.uuid4()),
        'sent_time': time_now()
    }
    msg: BasicMessageRecord = BasicMessageRecord.deserialize(sent_msg)

    # save it
    context: AdminRequestContext = request["context"]
    profile = context.profile
    try:
        async with profile.session() as session:
            await msg.save(session, reason="New sent message")
            LOGGER.info(msg)
    except Exception as err:
        LOGGER.error(err)
        raise err
    # LOGGER.info("< v0_1_connections_send_message")
    return response


@docs(
    tags=["basicmessage"],
    summary="Query agent-to-agent messages",
)
@querystring_schema(BasicMessageListQueryStringSchema())
@response_schema(BasicMessageListSchema(), 200, description="")
async def messages_list(request: web.BaseRequest):
    """
    Request handler for searching basic message records.

    Args:
        request: aiohttp request object

    Returns:
        The message list response

    """
    context: AdminRequestContext = request["context"]

    tag_filter = {}
    post_filter = {}

    state = request.query.get("state")
    if state:
        post_filter["state"] = state

    profile = context.profile
    try:
        async with profile.session() as session:
            records = await BasicMessageRecord.query(
                session, tag_filter, post_filter_positive=post_filter, alt=True
            )
        results = [record.serialize() for record in records]
        results.sort(key=messages_sort_key)
    except (StorageError, BaseModelError) as err:
        raise web.HTTPBadRequest(reason=err.roll_up) from err

    return web.json_response({"results": results})


async def register(app: web.Application):
    """Register routes."""
    app.add_routes(
        [
            web.get("/connections/{conn_id}/messages", messages_list, allow_head=False),
            web.post("/connections/{conn_id}/send-message", v0_1_connections_send_message)
        ]
    )


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
