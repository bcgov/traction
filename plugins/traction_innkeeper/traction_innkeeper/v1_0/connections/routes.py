import logging

from aiohttp import web
from aiohttp_apispec import docs, match_info_schema, response_schema
from acapy_agent.admin.decorators.auth import tenant_authentication
from acapy_agent.admin.request_context import AdminRequestContext
from acapy_agent.connections.models.conn_record import ConnRecord
from acapy_agent.messaging.models.base import BaseModelError
from acapy_agent.protocols.connections.v1_0.routes import (
    ConnectionsConnIdMatchInfoSchema, InvitationResultSchema)
from acapy_agent.storage.error import StorageNotFoundError
from marshmallow import fields 

LOGGER = logging.getLogger(__name__)

class InvitationResponseSchema(InvitationResultSchema):
    """Response schema for a previous connection invitation."""

    alias = fields.Str(
        required=False,
        allow_none=True,
        metadata={"description": "Optional alias for the connection", "example": "Bob"},
    )

@docs(tags=["connection"], summary="Fetch connection invitation")
@match_info_schema(ConnectionsConnIdMatchInfoSchema())
@response_schema(InvitationResponseSchema(), 200, description="")
@tenant_authentication
async def connections_invitation(request: web.BaseRequest):
    """Handle fetching invitation associated with a single connection record."""
    context: AdminRequestContext = request["context"]
    connection_id = request.match_info["conn_id"]

    profile = context.profile
    base_url = profile.settings.get("invite_base_url")

    if not base_url:
        base_url = profile.settings.get("default_endpoint")
        if base_url:
            LOGGER.debug(
                "Using 'default_endpoint' as base URL for invitation because 'invite_base_url' is not configured."
            )
        else:
            LOGGER.debug(
                "Neither 'invite_base_url' nor 'default_endpoint' are configured. Invitation URL might be incomplete."
            )
            base_url = ""

    try:
        async with profile.session() as session:
            connection = await ConnRecord.retrieve_by_id(session, connection_id)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err
    except BaseModelError as err:
        raise web.HTTPBadRequest(reason=err.roll_up) from err

    try:
        async with profile.session() as session:
            invitation = await connection.retrieve_invitation(session)
    except StorageNotFoundError:
        # if connection is a result of multi-use, then there is no invitation
        # ... go grab the multi-use connection's invitation
        try:
            async with profile.session() as session:
                multi_use = await ConnRecord.retrieve_by_invitation_key(
                    session, connection.invitation_key
                )
                invitation = await multi_use.retrieve_invitation(session)
        except StorageNotFoundError as err:
            raise web.HTTPNotFound(reason=err.roll_up) from err
        except BaseModelError as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err

    invitation_url = invitation.to_url(base_url) # Let's see what to_url produces

    # Always prepend base_url if to_url returns only query params
    if invitation_url.startswith("?"): # Check if to_url returned only query params
        constructed_invitation_url = f"{base_url}{invitation_url}"
    else:
        constructed_invitation_url = invitation_url # Assume to_url worked correctly

    result = {
        "connection_id": connection_id,
        "invitation": invitation.serialize(),
        "invitation_url": constructed_invitation_url,
    }
    if connection.alias:
        result["alias"] = connection.alias

    return web.json_response(result)


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    app.add_routes(
        [
            web.get(
                "/connections/{conn_id}/invitation",
                connections_invitation,
                allow_head=False,
            ),
        ]
    )
    LOGGER.info("< registering routes")


def post_process_routes(app: web.Application):
    pass