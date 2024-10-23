import functools
import logging

from aiohttp import web
from aiohttp_apispec import docs, response_schema, request_schema
from acapy_agent.admin.request_context import AdminRequestContext
from acapy_agent.connections.models.conn_record import ConnRecordSchema
from acapy_agent.messaging.models.base import BaseModelError
from acapy_agent.messaging.models.openapi import OpenAPISchema
from acapy_agent.protocols.didexchange.v1_0.manager import DIDXManagerError
from acapy_agent.protocols.endorse_transaction.v1_0.routes import (
    EndorserInfoSchema,
)

from acapy_agent.storage.error import StorageNotFoundError, StorageError
from acapy_agent.wallet.error import WalletError
from acapy_agent.admin.decorators.auth import tenant_authentication
from marshmallow import fields

from .endorser_connection_service import EndorserConnectionService
from ..tenant.routes import SWAGGER_CATEGORY
from ..innkeeper.tenant_manager import TenantManager
from ..innkeeper.models import TenantRecord

LOGGER = logging.getLogger(__name__)


def error_handler(func):
    @functools.wraps(func)
    async def wrapper(request):
        try:
            ret = await func(request)
            return ret
        except StorageNotFoundError as err:
            raise web.HTTPNotFound(reason=err.roll_up) from err
        except (StorageError, WalletError, DIDXManagerError, BaseModelError) as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err
        except Exception as err:
            LOGGER.error(err)
            raise err

    return wrapper


# class EndorserLedgerRequestSchema(OpenAPISchema):
#     """Request schema for endorser/ledger configuration."""

#     ledger_id = fields.Str(
#         required=True,
#         description="Ledger identifier",
#     )


class EndorserInfoResponseSchema(OpenAPISchema):
    """Response schema for endorser information/configuration."""

    endorser_name = fields.Str(
        required=True,
        description="Alias/name for endorser connection",
    )

    endorser_did = fields.Str(
        required=True,
        description="Alias/name for endorser connection",
    )


@docs(tags=[SWAGGER_CATEGORY], summary="Set connection with configured endorser")
# @request_schema(EndorserLedgerRequestSchema)
@response_schema(ConnRecordSchema(), 200, description="")
@error_handler
@tenant_authentication
async def endorser_connection_set(request: web.BaseRequest):
    """
    Request handler for creating and sending a request to a configured endorser

    Args:
        request: aiohttp request object

    Returns:
        The resulting connection record details

    """
    context: AdminRequestContext = request["context"]
    tenant_wallet_id = context.profile.settings.get("wallet.id")
    tenant_mgr = context.inject(TenantManager)
    root_profile = tenant_mgr.profile
    profile = context.profile
    async with root_profile.session() as session:
        tenant_record = await TenantRecord.query_by_wallet_id(session, tenant_wallet_id)
    # issuer check
    if (
        not tenant_record.connected_to_endorsers
        or not tenant_record.created_public_did
        or (
            tenant_record.connected_to_endorsers
            and tenant_record.connected_to_endorsers == []
        )
        or (tenant_record.created_public_did and tenant_record.created_public_did == [])
    ):
        raise web.HTTPBadRequest(
            reason=(
                "Tenant is not configured as an issuer, cannot "
                "connect with endorser or create public did"
            )
        )
    endorser_srv = context.inject(EndorserConnectionService)
    info = endorser_srv.endorser_info(profile)
    if not info:
        raise web.HTTPConflict(reason="Endorser is not configured")

    request = await endorser_srv.connect_with_endorser(profile, context.injector)

    return web.json_response(request.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
    summary="Get connection with configured endorser",
)
@response_schema(ConnRecordSchema(), 200)
@error_handler
@tenant_authentication
async def endorser_connection_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile

    endorser_srv = context.inject_or(EndorserConnectionService)

    rec = await endorser_srv.endorser_connection(profile)
    if not rec:
        raise web.HTTPNotFound(reason="Connection with endorser not found")

    return web.json_response(rec.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
    summary="Get configured endorser information",
)
@response_schema(EndorserInfoSchema(), 200)
@error_handler
@tenant_authentication
async def endorser_info_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    profile = context.profile

    endorser_srv = context.inject_or(EndorserConnectionService)

    info = endorser_srv.endorser_info(profile)
    if not info:
        raise web.HTTPNotFound(reason="Configured Endorser Information not found.")

    return web.json_response(info)


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    app.add_routes(
        [
            web.post("/tenant/endorser-connection", endorser_connection_set),
            web.get(
                "/tenant/endorser-connection", endorser_connection_get, allow_head=False
            ),
            web.get("/tenant/endorser-info", endorser_info_get, allow_head=False),
        ]
    )
    LOGGER.info("< registering routes")
