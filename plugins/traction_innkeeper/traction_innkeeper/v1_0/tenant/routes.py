import logging

import requests
from aiohttp import web
from aiohttp_apispec import (
    docs,
    response_schema,
    querystring_schema,
    request_schema,
)
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.valid import (
    INDY_DID,
    INDY_RAW_PUBLIC_KEY,
)
from aries_cloudagent.multitenant.admin.routes import (
    format_wallet_record,
    UpdateWalletRequestSchema,
)
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.wallet.base import BaseWallet
from aries_cloudagent.wallet.error import WalletError
from aries_cloudagent.wallet.models.wallet_record import (
    WalletRecordSchema,
    WalletRecord,
)

from marshmallow import fields

from ..routes import error_handler
from ..tenant_manager import TenantManager
from ..models import (
    TenantRecord,
    TenantRecordSchema,
)

LOGGER = logging.getLogger(__name__)

SWAGGER_CATEGORY = "traction-tenant"


class RegisterPublicDidSchema(OpenAPISchema):
    """Query string parameters and validators for register ledger nym request."""

    did = fields.Str(
        description="DID to register",
        required=True,
        **INDY_DID,
    )
    verkey = fields.Str(
        description="Verification key", required=True, **INDY_RAW_PUBLIC_KEY
    )
    alias = fields.Str(
        description="Alias",
        required=False,
        example="Barry",
    )


@docs(
    tags=[SWAGGER_CATEGORY],
)
@response_schema(TenantRecordSchema(), 200, description="")
@error_handler
async def tenant_self(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    # we need the caller's wallet id
    wallet_id = context.profile.settings.get("wallet.id")

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        # tenant's must always fetch by their wallet id.
        rec = await TenantRecord.query_by_wallet_id(session, wallet_id)
        LOGGER.info(rec)

    return web.json_response(rec.serialize())


@docs(tags=[SWAGGER_CATEGORY], summary="Register a Public DID")
@querystring_schema(RegisterPublicDidSchema())
@response_schema(schema=RegisterPublicDidSchema, code=200, description="")
@error_handler
async def register_public_did(request: web.BaseRequest):
    LOGGER.info("> tenant_register_public_did()")
    context: AdminRequestContext = request["context"]

    # check if there is a public did
    info = None
    async with context.session() as session:
        wallet = session.inject_or(BaseWallet)
        if not wallet:
            raise web.HTTPForbidden(reason="No wallet available")
        try:
            info = await wallet.get_public_did()
        except WalletError as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err
    if info:
        raise web.HTTPConflict(reason=f"Wallet already has a public DID: `{info.did}`")

    did = request.query.get("did")
    verkey = request.query.get("verkey")
    if not did or not verkey:
        raise web.HTTPBadRequest(
            reason="Request query must include both did and verkey"
        )

    alias = request.query.get("alias")
    if not alias:
        alias = context.profile.settings.get("wallet.id")

    genesis_url = context.profile.settings.get("ledger.genesis_url")
    did_registration_url = genesis_url.replace("genesis", "register")
    data = {
        "did": did,
        "verkey": verkey,
        "alias": alias,
    }
    requests.post(did_registration_url, json=data)
    LOGGER.info(f"did_registration_url = {did_registration_url}, data = {data}")

    LOGGER.info("< tenant_register_public_did()")
    return web.json_response(data)


@docs(tags=[SWAGGER_CATEGORY], summary="Get a tenant subwallet")
@response_schema(WalletRecordSchema(), 200, description="")
@error_handler
async def tenant_wallet_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    # we need the caller's wallet id
    wallet_id = context.profile.settings.get("wallet.id")

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    # this is from multitenant / admin / routes.py -> wallet_get
    # duplicate code.
    async with profile.session() as session:
        wallet_record = await WalletRecord.retrieve_by_id(session, wallet_id)
    result = format_wallet_record(wallet_record)

    return web.json_response(result)


@docs(tags=[SWAGGER_CATEGORY], summary="Update tenant wallet")
@request_schema(UpdateWalletRequestSchema)
@response_schema(WalletRecordSchema(), 200, description="")
@error_handler
async def tenant_wallet_update(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    # we need the caller's wallet id
    wallet_id = context.profile.settings.get("wallet.id")

    # this is from multitenant / admin / routes.py -> wallet_update
    # (mostly) duplicate code.
    body = await request.json()
    wallet_webhook_urls = body.get("wallet_webhook_urls")
    wallet_dispatch_type = body.get("wallet_dispatch_type")
    label = body.get("label")
    image_url = body.get("image_url")

    if all(
        v is None for v in (wallet_webhook_urls, wallet_dispatch_type, label, image_url)
    ):
        raise web.HTTPBadRequest(reason="At least one parameter is required.")

    # adjust wallet_dispatch_type according to wallet_webhook_urls
    if wallet_webhook_urls and wallet_dispatch_type is None:
        wallet_dispatch_type = "both"  # change from copied code (default)
    if wallet_webhook_urls == []:
        wallet_dispatch_type = "base"

    # only parameters that are not none are updated
    settings = {}
    if wallet_webhook_urls is not None:
        settings["wallet.webhook_urls"] = wallet_webhook_urls
    if wallet_dispatch_type is not None:
        settings["wallet.dispatch_type"] = wallet_dispatch_type
    if label is not None:
        settings["default_label"] = label
    if image_url is not None:
        settings["image_url"] = image_url

    multitenant_mgr = context.profile.inject(BaseMultitenantManager)
    wallet_record = await multitenant_mgr.update_wallet(wallet_id, settings)
    result = format_wallet_record(wallet_record)

    return web.json_response(result)


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    # routes that require a tenant token.
    app.add_routes(
        [
            web.get("/tenant", tenant_self, allow_head=False),
            web.post("/tenant/register-public-did", register_public_did),
            web.get("/tenant/wallet", tenant_wallet_get, allow_head=False),
            web.put("/tenant/wallet", tenant_wallet_update),
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
            "description": "Traction Tenant - tenant self administration (traction_innkeeper v1_0 plugin)",
        }
    )
