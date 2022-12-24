import logging

from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.multitenant.admin.routes import (
    CreateWalletTokenRequestSchema,
    CreateWalletTokenResponseSchema,
    CreateWalletRequestSchema,
    CreateWalletResponseSchema,
    wallet_create,
)
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.multitenant.error import WalletKeyMissingError
from aries_cloudagent.storage.error import StorageNotFoundError
from aries_cloudagent.wallet.models.wallet_record import WalletRecord
from marshmallow import fields, validate, validates_schema, ValidationError

from .config import MultitenantProviderConfig
from .manager import WalletKeyMismatchError

LOGGER = logging.getLogger(__name__)


class PluginCreateWalletRequestSchema(CreateWalletRequestSchema):
    """Request schema for adding a new wallet which will be registered by the agent."""

    key_management_mode = fields.Str(
        description="Key management method to use for this wallet.",
        example=WalletRecord.MODE_MANAGED,
        default=WalletRecord.MODE_MANAGED,
        validate=validate.OneOf(
            (
                WalletRecord.MODE_MANAGED,
                WalletRecord.MODE_UNMANAGED,
            )
        ),
    )

    @validates_schema
    def validate_fields(self, data, **kwargs):
        """
        Validate schema fields.

        Args:
            data: The data to validate

        Raises:
            ValidationError: If any of the fields do not validate

        """

        if data.get("wallet_type") in ["indy", "askar"]:
            for field in ("wallet_key", "wallet_name"):
                if field not in data:
                    raise ValidationError("Missing required field", field)


@docs(
    tags=["multitenancy"],
    summary="Create a subwallet (multitenant_provider plugin override)",
)
@request_schema(PluginCreateWalletRequestSchema)
@response_schema(CreateWalletResponseSchema(), 200, description="")
async def plugin_wallet_create(request: web.BaseRequest):
    """
    Request handler for adding a new subwallet for handling by the agent.

    Args:
        request: aiohttp request object
    """

    # we are just overriding the validation (allow unmanaged mode, expect askar to have a wallet key)
    # so use the existing create_wallet call
    return await wallet_create(request)


@docs(
    tags=["multitenancy"],
    summary="Get auth token for a subwallet (multitenant_provider plugin override)",
)
@request_schema(CreateWalletTokenRequestSchema)
@response_schema(CreateWalletTokenResponseSchema(), 200, description="")
async def plugin_wallet_create_token(request: web.BaseRequest):
    """
    Request handler for creating an authorization token for a specific subwallet.

    Args:
        request: aiohttp request object
    """

    context: AdminRequestContext = request["context"]
    wallet_id = request.match_info["wallet_id"]
    wallet_key = None

    LOGGER.debug(f"wallet_id = {wallet_id}")

    # "builtin" wallet_create_token uses request.has_body / can_read_body
    # which do not always return true, so wallet_key wasn't getting set or passed
    # into create_auth_token.

    if request.body_exists:
        body = await request.json()
        wallet_key = body.get("wallet_key")
        LOGGER.debug(f"wallet_key = {wallet_key}")

    profile = context.profile
    config = profile.inject(MultitenantProviderConfig)
    try:
        multitenant_mgr = profile.inject(BaseMultitenantManager)
        async with profile.session() as session:
            wallet_record = await WalletRecord.retrieve_by_id(session, wallet_id)

        # this logic is weird, a managed wallet cannot pass in a key.
        # i guess this means that a controller determines who can call this endpoint?
        # and there is some other way of ensuring the caller is using the correct wallet_id?

        if (not wallet_record.requires_external_key) and wallet_key:
            if config.errors.on_unneeded_wallet_key:
                raise web.HTTPBadRequest(
                    reason=f"Wallet {wallet_id} doesn't require the wallet key to be provided"
                )
            else:
                LOGGER.warning(
                    f"Wallet {wallet_id} doesn't require the wallet key but one was provided"
                )
                wallet_key = None

        token = await multitenant_mgr.create_auth_token(wallet_record, wallet_key)
    except StorageNotFoundError as err:
        raise web.HTTPNotFound(reason=err.roll_up) from err
    except WalletKeyMissingError as err:
        raise web.HTTPUnauthorized(reason=err.roll_up) from err
    except WalletKeyMismatchError as err:
        raise web.HTTPConflict(reason=err.roll_up) from err

    return web.json_response({"token": token})


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")

    # we need to replace the current multitenant endpoints...
    # 1) to allow unmanaged wallets
    has_wallet_create = False
    # 2) and to ensure that we pass along the wallet key
    has_wallet_create_token = False
    for r in app.router.routes():
        if r.method == "POST":
            if r.resource and r.resource.canonical == "/multitenancy/wallet":
                LOGGER.info(
                    f"found route: {r.method} {r.resource.canonical} ({r.handler})"
                )
                LOGGER.info(f"... replacing current handler: {r.handler}")
                r._handler = plugin_wallet_create
                LOGGER.info(f"... with new handler: {r.handler}")
                has_wallet_create = True
            if (
                r.resource
                and r.resource.canonical == "/multitenancy/wallet/{wallet_id}/token"
            ):
                LOGGER.info(
                    f"found route: {r.method} {r.resource.canonical} ({r.handler})"
                )
                LOGGER.info(f"... replacing current handler: {r.handler}")
                r._handler = plugin_wallet_create_token
                LOGGER.info(f"... with new handler: {r.handler}")
                has_wallet_create_token = True

    # ok, just in case we get loaded before the builtin multitenant (should be impossible)
    # let's make sure we've added endpoints we expect
    if not has_wallet_create:
        LOGGER.info(f"adding POST /multitenancy/wallet route")
        app.add_routes(
            [
                web.post("/multitenancy/wallet", plugin_wallet_create),
            ]
        )
    if not has_wallet_create_token:
        LOGGER.info(f"adding POST /multitenancy/wallet/<wallet_id>/token route")
        app.add_routes(
            [
                web.post(
                    "/multitenancy/wallet/{wallet_id}/token", plugin_wallet_create_token
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
        {"name": "multitenancy", "description": "Multitenant wallet management"}
    )
