import logging

from aiohttp import web
from aiohttp_apispec import (
    docs,
    match_info_schema,
    response_schema,
    request_schema,
)
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.admin.server import AdminConfigSchema
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.multitenant.admin.routes import (
    format_wallet_record,
    UpdateWalletRequestSchema,
    get_extra_settings_dict_per_tenant,
)
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.storage.error import StorageNotFoundError
from aries_cloudagent.version import __version__
from aries_cloudagent.wallet.models.wallet_record import (
    WalletRecordSchema,
    WalletRecord,
)
from marshmallow import fields, validate

from ..innkeeper.routes import (
    error_handler,
    TenantAuthenticationApiIdMatchInfoSchema,
    TenantAuthenticationApiListSchema,
    TenantAuthenticationApiRecordSchema,
    TenantAuthenticationsApiResponseSchema,
    TenantAuthenticationApiOperationResponseSchema,
)
from ..innkeeper.tenant_manager import TenantManager
from ..innkeeper.models import (
    TenantAuthenticationApiRecord,
    TenantRecord,
    TenantRecordSchema,
)
from ..innkeeper.utils import create_api_key, TenantConfigSchema, TenantApiKeyException

LOGGER = logging.getLogger(__name__)

SWAGGER_CATEGORY = "traction-tenant"


class CustomUpdateWalletRequestSchema(UpdateWalletRequestSchema):
    image_url = fields.Str(
        description="Image url for this wallet. This image url is publicized\
            (self-attested) to other agents as part of forming a connection.",
        example="https://aries.ca/images/sample.png",
        validate=validate.URL(),
    )


class UpdateContactRequestSchema(OpenAPISchema):
    contact_email = fields.Str(
        description="The new email to associate with this tenant.",
        example="example@exampleserver.com",
        validate=validate.Email(),
    )


class TenantApiKeyRequestSchema(OpenAPISchema):
    """Request schema for api auth record."""

    alias = fields.Str(
        required=True,
        description="Alias/label",
        example="API key for my Tenant",
    )


class TenantLedgerIdConfigSchema(OpenAPISchema):
    ledger_id = fields.Str(
        description="Ledger identifier",
        required=True,
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
    tenant_issuer_flag = tenant_record.auto_issuer
    enable_ledger_switch = tenant_record.enable_ledger_switch
    curr_ledger_id = tenant_record.curr_ledger_id
    return web.json_response(
        {
            "connect_to_endorser": endorser_config,
            "create_public_did": public_did_config,
            "auto_issuer": tenant_issuer_flag,
            "enable_ledger_switch": enable_ledger_switch,
            "curr_ledger_id": curr_ledger_id,
        }
    )


@docs(tags=[SWAGGER_CATEGORY], summary="Set tenant curr_ledger_id setting")
@request_schema(TenantLedgerIdConfigSchema)
@response_schema(TenantLedgerIdConfigSchema(), 200, description="")
@error_handler
async def tenant_config_ledger_id_set(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    wallet_id = context.profile.settings.get("wallet.id")
    body = await request.json()
    curr_ledger_id = body.get("ledger_id")
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    async with profile.session() as session:
        tenant_record = await TenantRecord.query_by_wallet_id(session, wallet_id)
        if curr_ledger_id:
            tenant_record.curr_ledger_id = curr_ledger_id
        await tenant_record.save(session)
    return web.json_response(
        {
            "ledger_id": curr_ledger_id,
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


@docs(tags=[SWAGGER_CATEGORY], summary="Update tenant email")
@request_schema(UpdateContactRequestSchema)
@response_schema(UpdateContactRequestSchema, 200, description="")
@error_handler
async def tenant_email_update(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    # we need the caller's wallet id
    wallet_id = context.profile.settings.get("wallet.id")

    # this is from multitenant / admin / routes.py -> wallet_update
    # (mostly) duplicate code.
    body: dict = await request.json()
    contact_email = body["contact_email"]

    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        rec = await TenantRecord.query_by_wallet_id(session, wallet_id)
        rec.contact_email = contact_email
        await rec.save(session, reason="updated email")

    return web.json_response(body)


@docs(tags=[SWAGGER_CATEGORY], summary="Create API Key Record")
@request_schema(TenantApiKeyRequestSchema())
@response_schema(TenantAuthenticationsApiResponseSchema(), 200, description="")
@error_handler
async def tenant_api_key(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    wallet_id = context.profile.settings.get("wallet.id")

    # keys are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        # use the id from the Tenant record and fetch associated api keys
        rec = await TenantRecord.query_by_wallet_id(session, wallet_id)
        LOGGER.debug(rec)
        tenant_id = rec.tenant_id

    try:
        body = await request.json()
        body["tenant_id"] = tenant_id
        rec: TenantAuthenticationApiRecord = TenantAuthenticationApiRecord(**body)
        api_key, tenant_authentication_api_id = await create_api_key(rec, mgr)
    except TenantApiKeyException as err:
        raise web.HTTPConflict(reason=str(err))

    return web.json_response(
        {
            "tenant_authentication_api_id": tenant_authentication_api_id,
            "api_key": api_key,
        }
    )


@docs(tags=[SWAGGER_CATEGORY], summary="Read API Key Record")
@match_info_schema(TenantAuthenticationApiIdMatchInfoSchema())
@response_schema(TenantAuthenticationApiRecordSchema(), 200, description="")
@error_handler
async def tenant_api_key_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    wallet_id = context.profile.settings.get("wallet.id")
    tenant_authentication_api_id = request.match_info["tenant_authentication_api_id"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        # use the id from the Tenant record and fetch associated api key
        rec = await TenantRecord.query_by_wallet_id(session, wallet_id)
        LOGGER.debug(rec)
        tenant_id = rec.tenant_id

        rec = await TenantAuthenticationApiRecord.retrieve_by_auth_api_id(
            session, tenant_authentication_api_id
        )
        LOGGER.info(rec)

        # if rec tenant_id does not match the tenant_id from the wallet, raise 404
        if rec.tenant_id != tenant_id:
            raise web.HTTPNotFound(reason="No such record")

    return web.json_response(rec.serialize())


@docs(tags=[SWAGGER_CATEGORY], summary="List tenant API Key Records")
@response_schema(TenantAuthenticationApiListSchema(), 200, description="")
@error_handler
async def tenant_api_key_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    wallet_id = context.profile.settings.get("wallet.id")

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        # use the id from the Tenant record and fetch associated api keys
        rec = await TenantRecord.query_by_wallet_id(session, wallet_id)
        LOGGER.debug(rec)
        tenant_id = rec.tenant_id

        records = await TenantAuthenticationApiRecord.query_by_tenant_id(
            session, tenant_id
        )
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


@docs(tags=[SWAGGER_CATEGORY], summary="Delete API Key")
@match_info_schema(TenantAuthenticationApiIdMatchInfoSchema)
@response_schema(TenantAuthenticationApiOperationResponseSchema, 200, description="")
@error_handler
async def tenant_api_key_delete(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    wallet_id = context.profile.settings.get("wallet.id")
    tenant_authentication_api_id = request.match_info["tenant_authentication_api_id"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    result = False
    async with profile.session() as session:
        # use the id from the Tenant record and fetch associated api key
        rec = await TenantRecord.query_by_wallet_id(session, wallet_id)
        LOGGER.debug(rec)
        tenant_id = rec.tenant_id

        rec = await TenantAuthenticationApiRecord.retrieve_by_auth_api_id(
            session, tenant_authentication_api_id
        )
        LOGGER.debug(rec)

        # if rec tenant_id does not match the tenant_id from the wallet, raise 404
        if rec.tenant_id != tenant_id:
            raise web.HTTPNotFound(reason="No such record")

        await rec.delete_record(session)

        try:
            await TenantAuthenticationApiRecord.retrieve_by_auth_api_id(
                session, tenant_authentication_api_id
            )
        except StorageNotFoundError:
            # this is to be expected... do nothing, do not log
            result = True

    return web.json_response({"success": result})


@docs(tags=[SWAGGER_CATEGORY], summary="Fetch the server configuration")
@response_schema(AdminConfigSchema(), 200, description="")
@error_handler
async def tenant_server_config_handler(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    # use base/root profile for server config, use Tenant Manager profile
    # this is to not get the Innkeeper tenant's config, but the server cfg
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    config = {
        k: (
           profile.context.settings[k]
        )
        for k in profile.context.settings
        if k
        not in [
            "default_label",
            "admin.admin_api_key",
            "admin.admin_insecure_mode",
            "admin.enabled",
            "admin.host",
            "admin.port",
            "admin.webhook_urls",
            "admin.admin_client_max_request_size",
            "multitenant.jwt_secret",
            "wallet.key",
            "wallet.name",
            "multitenant.wallet_name",
            "wallet.storage_type",
            "wallet.storage_config",
            "wallet.rekey",
            "wallet.seed",
            "wallet.storage_creds",
        ]
    }
    try:
      del config["plugin_config"]["traction_innkeeper"]["innkeeper_wallet"]
      config["config"]["ledger.ledger_config_list"] = [
        {k: v for k, v in d.items() if k != "genesis_transactions"}
        for d in config["config"]["ledger.ledger_config_list"]
      ]
    except KeyError as e:
      LOGGER.warn(f"The key to be removed: '{e.args[0]}' is missing from the dictionary.")
    config["version"] = __version__

    return web.json_response({"config": config})


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    # routes that require a tenant token.
    app.add_routes(
        [
            web.get("/tenant", tenant_self, allow_head=False),
            web.get("/tenant/wallet", tenant_wallet_get, allow_head=False),
            web.put("/tenant/wallet", tenant_wallet_update),
            web.put("/tenant/contact_email", tenant_email_update),
            web.get("/tenant/config", tenant_config_get, allow_head=False),
            web.put("/tenant/config/set-ledger-id", tenant_config_ledger_id_set),
            web.post("/tenant/authentications/api", tenant_api_key),
            web.get(
                "/tenant/authentications/api/", tenant_api_key_list, allow_head=False
            ),
            web.get(
                "/tenant/authentications/api/{tenant_authentication_api_id}",
                tenant_api_key_get,
                allow_head=False,
            ),
            web.delete(
                "/tenant/authentications/api/{tenant_authentication_api_id}",
                tenant_api_key_delete,
            ),
            web.get(
                "/tenant/server/status/config", 
                tenant_server_config_handler, 
                allow_head=False
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
            "name": SWAGGER_CATEGORY,
            "description": "Traction Tenant - tenant self administration (traction_innkeeper v1_0 plugin)",
        }
    )
