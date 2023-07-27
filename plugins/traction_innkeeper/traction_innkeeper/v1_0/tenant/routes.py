import logging

from aiohttp import web
from aiohttp_apispec import (
    docs,
    response_schema,
    request_schema,
)
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.multitenant.admin.routes import (
    format_wallet_record,
    UpdateWalletRequestSchema,
    get_extra_settings_dict_per_tenant,
)
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.wallet.models.wallet_record import (
    WalletRecordSchema,
    WalletRecord,
)
from marshmallow import fields, validate

from ..innkeeper.routes import error_handler
from ..innkeeper.tenant_manager import TenantManager
from ..innkeeper.models import (
    TenantRecord,
    TenantRecordSchema,
)
from ..innkeeper.utils import TenantConfigSchema

LOGGER = logging.getLogger(__name__)

SWAGGER_CATEGORY = "traction-tenant"


class CustomUpdateWalletRequestSchema(UpdateWalletRequestSchema):
    image_url = fields.Str(
        description="Image url for this wallet. This image url is publicized\
            (self-attested) to other agents as part of forming a connection.",
        example="https://aries.ca/images/sample.png",
        validate=validate.URL(),
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


@docs(tags=[SWAGGER_CATEGORY], summary="Get tenant setting")
@response_schema(TenantConfigSchema(), 200, description="")
@error_handler
async def tenant_config_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    wallet_id = context.profile.settings.get("wallet.id")
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    async with profile.session() as session:
        tenant_record = await TenantRecord.query_by_wallet_id(session, wallet_id)
    endorser_config = tenant_record.connected_to_endorsers
    public_did_config = tenant_record.created_public_did
    tenant_issuer_flag = tenant_record.self_issuer_permission
    return web.json_response(
        {
            "connect_to_endorser": endorser_config,
            "create_public_did": public_did_config,
            "self_issuer_permission": tenant_issuer_flag,
        }
    )


@docs(tags=[SWAGGER_CATEGORY], summary="Update tenant wallet")
@request_schema(CustomUpdateWalletRequestSchema)
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
    extra_settings = body.get("extra_settings") or {}

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
    if "ACAPY_ENDORSER_ROLE" in extra_settings:
        if extra_settings.get("ACAPY_ENDORSER_ROLE") == "author":
            settings["endorser.endorser"] = False
        elif extra_settings.get("ACAPY_ENDORSER_ROLE") == "endorser":
            settings["endorser.author"] = False
            settings["endorser.auto_request"] = False
            settings["endorser.auto_write"] = False
        elif extra_settings.get("ACAPY_ENDORSER_ROLE") == "none":
            settings["endorser.author"] = False
            settings["endorser.endorser"] = False
            settings["endorser.auto_request"] = False
            settings["endorser.auto_write"] = False
    settings.update(get_extra_settings_dict_per_tenant(extra_settings))
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
            web.get("/tenant/wallet", tenant_wallet_get, allow_head=False),
            web.put("/tenant/wallet", tenant_wallet_update),
            web.get("/tenant/config", tenant_config_get, allow_head=False),
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
