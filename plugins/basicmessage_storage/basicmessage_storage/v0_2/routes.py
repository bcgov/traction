import logging
import re
import typing
import uuid

from aiohttp import web
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.messaging.util import time_now
from aries_cloudagent.messaging.valid import UUIDFour
from aries_cloudagent.protocols.basicmessage.v1_0.message_types import SPEC_URI
from frozenlist import FrozenList

from ..v0_1.models import BasicMessageRecord
from ..v0_1.routes import messages_list

LOGGER = logging.getLogger(__name__)

SAVE_MESSAGE_PATTERN = re.compile(f"^/connections/(?:{UUIDFour.PATTERN})/send-message$")


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


async def register(app: web.Application):
    """Register routes."""

    # we are not adding a custom route since we are not changing the interface.
    # put some middleware that will do our work: save a record.
    app._middlewares = FrozenList(
        app.middlewares[:] + [save_message_middleware]
    )

    # add in the message list route, no need to re-write it though.
    app.add_routes(
        [
            web.get("/connections/{conn_id}/messages", messages_list, allow_head=False)
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
