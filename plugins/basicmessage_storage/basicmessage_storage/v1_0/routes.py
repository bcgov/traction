import logging
import re
import typing
import uuid

from aiohttp import web
from aiohttp_apispec import docs, response_schema, querystring_schema
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.util import time_now
from aries_cloudagent.messaging.valid import UUIDFour
from aries_cloudagent.protocols.basicmessage.v1_0.message_types import SPEC_URI
from aries_cloudagent.storage.error import StorageError
from frozenlist import FrozenList
from marshmallow import fields, validate

from .models import BasicMessageRecord, BasicMessageRecordSchema

LOGGER = logging.getLogger(__name__)

SAVE_MESSAGE_PATTERN = re.compile(f"^/connections/(?:{UUIDFour.PATTERN})/send-message$")


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


def messages_sort_key(rec):
    """Get the sorting key for a basic messages."""
    if rec["state"] == BasicMessageRecord.STATE_SENT:
        pfx = "2"
    elif rec["state"] == BasicMessageRecord.STATE_RECV:
        pfx = "1"
    else:  # GRANTED
        pfx = "0"
    return pfx + rec["created_at"]


@web.middleware
async def save_message_middleware(
        request: web.BaseRequest, handler: typing.Coroutine
):
    path = request.path
    _intercept = re.fullmatch(SAVE_MESSAGE_PATTERN, path)
    if _intercept:
        LOGGER.info("> persistence_middleware")
        connection_id = request.match_info["conn_id"]
        params = await request.json()
        content = params["content"]

        response = await handler(request)

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
            LOGGER.info("< persistence_middleware")
        except Exception as err:
            LOGGER.error(err)
            raise err
    else:
        response = await handler(request)
    return response


@docs(
    tags=["basicmessage"],
    summary="Query messages from all agents (basicmessage_storage v1_0 plugin)",
)
@querystring_schema(BasicMessageListQueryStringSchema())
@response_schema(BasicMessageListSchema(), 200, description="")
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
                alt=True
            )
        results = [record.serialize() for record in records]
        results.sort(key=messages_sort_key)
    except (StorageError, BaseModelError) as err:
        raise web.HTTPBadRequest(reason=err.roll_up) from err

    return web.json_response({"results": results})


async def register(app: web.Application):
    """Register routes."""

    # we are not adding a custom route since we are not changing the interface.
    # put some middleware that will do our work: save a record.
    app._middlewares = FrozenList(
        app.middlewares[:] + [save_message_middleware]
    )

    # add in the message list(s) route
    app.add_routes(
        [
            web.get("/basicmessages", all_messages_list, allow_head=False)
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
