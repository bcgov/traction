import functools
import logging
import uuid

from aiohttp import ClientSession, web
from aiohttp_apispec import (
    docs,
    match_info_schema,
    request_schema,
    response_schema,
    use_kwargs,
)
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.admin.server import AdminConfigSchema
from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.valid import JSONWebToken, UUIDFour
from aries_cloudagent.multitenant.admin.routes import (
    CreateWalletTokenRequestSchema,
    CreateWalletTokenResponseSchema,
)
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.multitenant.error import WalletKeyMissingError
from aries_cloudagent.storage.error import StorageError, StorageNotFoundError
from aries_cloudagent.version import __version__
from aries_cloudagent.wallet.error import WalletSettingsError
from aries_cloudagent.wallet.models.wallet_record import WalletRecord
from marshmallow import fields, validate

from . import TenantManager
from .config import InnkeeperWalletConfig
from .utils import (
    approve_reservation,
    refresh_registration_token,
    create_api_key,
    EndorserLedgerConfigSchema,
    ReservationException,
    TenantApiKeyException,
    TenantConfigSchema,
)
from .models import (
    ReservationRecord,
    ReservationRecordSchema,
    TenantRecord,
    TenantRecordSchema,
    TenantAuthenticationApiRecord,
    TenantAuthenticationApiRecordSchema,
)

LOGGER = logging.getLogger(__name__)
SWAGGER_CATEGORY = "traction-innkeeper"


def innkeeper_only(func):
    @functools.wraps(func)
    async def wrapper(request):
        print("> innkeeper_only")
        context: AdminRequestContext = request["context"]
        profile = context.profile
        wallet_name = str(profile.settings.get("wallet.name"))
        wallet_innkeeper = bool(profile.settings.get("wallet.innkeeper"))
        LOGGER.info(f"wallet.name = {wallet_name}")
        LOGGER.info(f"wallet.innkeeper = {wallet_innkeeper}")
        if wallet_innkeeper:
            try:
                ret = await func(request)
                return ret
            finally:
                print("< innkeeper_only")
        else:
            LOGGER.error(
                f"API call is for innkeepers only. wallet.name = '{wallet_name}', wallet.innkeeper = {wallet_innkeeper}"
            )
            raise web.HTTPUnauthorized()

    return wrapper


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
        except (WalletSettingsError, StorageError, BaseModelError) as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err
        except Exception as err:
            # We do not want a hard dependency on multitenant_provider plugin.
            # It throws a WalletKeyMismatchError, so let's "soft" handle it.
            # That plugin throws a 409 when wallet_key is incorrect...
            if "WalletKeyMismatchError" == type(err).__name__:
                raise web.HTTPConflict(reason=err.roll_up) from err
            else:
                LOGGER.error(err)
                raise err

    return wrapper


# extending the CreateWalletTokenRequestSchema to allow for an API key
class CustomCreateWalletTokenRequestSchema(CreateWalletTokenRequestSchema):
    """Request schema for creating a wallet token."""

    api_key = fields.Str(
        description="API key for this wallet",
        required=False,
        example="3bd14a1e8fb645ddadf9913c0922ff3b",
    )


class DefaultConfigValuesSchema(OpenAPISchema):
    """Response schema for default config values."""

    connected_to_endorsers = fields.List(
        fields.Nested(EndorserLedgerConfigSchema()),
        description="Endorser config",
    )
    created_public_did = fields.List(
        fields.Str(
            description="Ledger identifier",
            required=False,
        ),
        description="Public DID config",
    )


class ReservationRequestSchema(OpenAPISchema):
    """Request schema for tenant reservation."""

    tenant_name = fields.Str(
        required=True,
        description="Proposed name of Tenant",
        example="line of business short name",
    )

    contact_email = fields.Str(
        required=True,
        description="Contact email for this tenant request",
    )

    context_data = fields.Dict(
        required=False,
        description="Optional context data for this tenant request",
        example={"contact_phone": "555-555-5555"},
    )


class ReservationResponseSchema(OpenAPISchema):
    """Response schema for tenant reservation."""

    reservation_id = fields.Str(
        required=True,
        description="The reservation record identifier",
        example=UUIDFour.EXAMPLE,
    )


class CheckinSchema(OpenAPISchema):
    """Request schema for reservation Check-in."""

    reservation_pwd = fields.Str(
        required=True,
        description="The reservation password",
        example=UUIDFour.EXAMPLE,
    )


class CheckinResponseSchema(OpenAPISchema):
    """Response schema for reservation Check-in."""

    wallet_id = fields.Str(
        description="Subwallet identifier", required=True, example=UUIDFour.EXAMPLE
    )
    wallet_key = fields.Str(
        description="Master key used for key derivation.", example="MySecretKey123"
    )
    token = fields.Str(
        description="Authorization token to authenticate wallet requests",
        example=JSONWebToken.EXAMPLE,
    )


class ReservationListSchema(OpenAPISchema):
    """Response schema for reservations list."""

    results = fields.List(
        fields.Nested(ReservationRecordSchema()),
        description="List of reservations",
    )


class ReservationIdMatchInfoSchema(OpenAPISchema):
    reservation_id = fields.Str(
        description="Reservation identifier", required=True, example=UUIDFour.EXAMPLE
    )


class ReservationApproveSchema(OpenAPISchema):
    """Request schema for tenant reservation approval."""


class ReservationRefreshSchema(OpenAPISchema):
    """Request schema for tenant reservation approval."""


class ReservationApproveResponseSchema(OpenAPISchema):
    """Response schema for tenant reservation approval."""

    reservation_pwd = fields.Str(
        required=True,
        description="The reservation password - deliver to tenant contact",
    )


class ReservationApproveRequestSchema(OpenAPISchema):
    """Request schema for tenant reservation approved/denied."""

    state_notes = fields.Str(
        required=False,
        description="Reason(s) for approving a tenant reservation",
        example="Welcome",
    )


class ReservationDenyRequestSchema(OpenAPISchema):
    """Request schema for tenant reservation approved/denied."""

    state_notes = fields.Str(
        required=True,
        description="Reason(s) for approving or denying a tenant reservation",
        example="No room at the inn.",
    )


class TenantIdMatchInfoSchema(OpenAPISchema):
    tenant_id = fields.Str(
        description="Tenant identifier", required=True, example=UUIDFour.EXAMPLE
    )


class TenantAuthenticationsApiRequestSchema(OpenAPISchema):
    """Request schema for api auth record."""

    tenant_id = fields.Str(
        required=True,
        description="Tenant ID",
        example=UUIDFour.EXAMPLE,
    )

    alias = fields.Str(
        required=True,
        description="Alias/label",
        example="API key for sample line of business",
    )


class TenantAuthenticationsApiResponseSchema(OpenAPISchema):
    """Response schema for api auth record."""

    tenant_authentication_api_id = fields.Str(
        required=True,
        description="The API key record identifier",
        example=UUIDFour.EXAMPLE,
    )

    api_key = fields.Str(
        required=True,
        description="The API key",
        example="3bd14a1e8fb645ddadf9913c0922ff3b",
    )


class TenantListSchema(OpenAPISchema):
    """Response schema for tenants list."""

    results = fields.List(
        fields.Nested(TenantRecordSchema()),
        description="List of tenants",
    )


class TenantListQuerySchema(OpenAPISchema):
    """Query parameters schema for tenants list."""

    state = fields.Str(
        required=False,
        description="The state of the tenants to filter by.",
        example=TenantRecord.STATE_ACTIVE,
        validate=validate.OneOf(
            [TenantRecord.STATE_ACTIVE, TenantRecord.STATE_DELETED, "all"]
        ),
    )


class TenantAuthenticationApiListSchema(OpenAPISchema):
    """Response schema for authentications - users list."""

    results = fields.List(
        fields.Nested(TenantAuthenticationApiRecordSchema()),
        description="List of reservations",
    )


class TenantAuthenticationApiIdMatchInfoSchema(OpenAPISchema):
    """Schema for finding a tenant auth user by the record ID."""

    tenant_authentication_api_id = fields.Str(
        description="Tenant authentication api key identifier",
        required=True,
        example=UUIDFour.EXAMPLE,
    )


class TenantAuthenticationApiOperationResponseSchema(OpenAPISchema):
    """Response schema for simple operations."""

    success = fields.Bool(
        required=True,
        description="True if operation successful, false if otherwise",
    )


@docs(
    tags=["multitenancy"],
)
@request_schema(ReservationRequestSchema())
@response_schema(ReservationResponseSchema(), 200, description="")
@error_handler
async def tenant_reservation(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    body = await request.json()
    rec: ReservationRecord = ReservationRecord(**body)

    # reservations are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        await rec.save(session, reason="New tenant reservation")
        LOGGER.info(rec)

    if mgr._config.reservation.auto_approve:
        LOGGER.info("Tenant auto-approve is on, approving newly created tenant")
        try:
            _pwd = await approve_reservation(rec.reservation_id, rec.state_notes, mgr)
            return web.json_response(
                {"reservation_id": rec.reservation_id, "reservation_pwd": _pwd}
            )
        except ReservationException as err:
            raise web.HTTPConflict(reason=str(err))

    return web.json_response({"reservation_id": rec.reservation_id})


@docs(
    tags=["multitenancy"],
)
@match_info_schema(ReservationIdMatchInfoSchema())
@response_schema(ReservationRecordSchema(), 200, description="")
@error_handler
async def tenant_reservation_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    reservation_id = request.match_info["reservation_id"]

    async with profile.session() as session:
        rec = await ReservationRecord.retrieve_by_reservation_id(
            session, reservation_id
        )
        LOGGER.info(rec)

    return web.json_response(rec.serialize())


@docs(
    tags=["multitenancy"],
)
@match_info_schema(ReservationIdMatchInfoSchema())
@request_schema(CheckinSchema())
@response_schema(CheckinResponseSchema(), 200, description="")
@error_handler
async def tenant_checkin(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    body = await request.json()

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    reservation_id = request.match_info["reservation_id"]

    async with profile.session() as session:
        res_rec = await ReservationRecord.retrieve_by_reservation_id(
            session, reservation_id
        )
        reservation_pwd = body.get("reservation_pwd")

        if res_rec.expired:
            raise web.HTTPUnauthorized(reason="Reservation has expired")

        if res_rec.state == ReservationRecord.STATE_APPROVED:
            reservation_token = mgr.check_reservation_password(reservation_pwd, res_rec)
            if not reservation_token:
                raise web.HTTPUnauthorized(reason="Reservation password incorrect")

            # ok, let's update this, create a tenant, create a wallet
            wallet_key = str(uuid.uuid4())
            settings_dict = {}
            if res_rec.connect_to_endorsers and len(res_rec.connect_to_endorsers) > 0:
                settings_dict["tenant.endorser_config"] = res_rec.connect_to_endorsers
            if res_rec.create_public_did and len(res_rec.create_public_did) > 0:
                settings_dict["tenant.public_did_config"] = res_rec.create_public_did
            tenant, wallet_record, token = await mgr.create_wallet(
                wallet_name=res_rec.tenant_name,
                wallet_key=wallet_key,
                tenant_email=res_rec.contact_email,
                extra_settings=settings_dict,
            )

            # update this reservation
            res_rec.state = ReservationRecord.STATE_CHECKED_IN
            res_rec.wallet_id = wallet_record.wallet_id
            res_rec.tenant_id = tenant.tenant_id
            # do not need reservation token data
            res_rec.reservation_token_hash = None
            res_rec.reservation_token_salt = None
            res_rec.reservation_token_expiry = None
            await res_rec.save(session)
        else:
            raise web.HTTPConflict(
                reason=f"Reservation state is currently '{res_rec.state}' and cannot be set to '{ReservationRecord.STATE_CHECKED_IN}'."
            )

    return web.json_response(
        {
            "wallet_id": wallet_record.wallet_id,
            "wallet_key": wallet_key,
            "token": token,
        }
    )


@docs(tags=["multitenancy"], summary="Get auth token for a tenant")
@match_info_schema(TenantIdMatchInfoSchema())
@request_schema(CustomCreateWalletTokenRequestSchema)
@response_schema(CreateWalletTokenResponseSchema(), 200, description="")
@error_handler
async def tenant_create_token(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    tenant_id = request.match_info["tenant_id"]
    wallet_key = None

    # If no body raise an error
    if not request.body_exists:
        raise web.HTTPUnauthorized(reason="Wallet Key or API Key not provided")

    body = await request.json()
    wallet_key = body.get("wallet_key")
    api_key = body.get("api_key")

    # If neither wallet_key or api_key provided raise an error
    if not wallet_key and not api_key:
        raise web.HTTPUnauthorized(reason="Wallet Key or API Key not provided")

    # If both wallet_key and api_key provided raise an error
    if wallet_key and api_key:
        raise web.HTTPUnprocessableEntity(
            reason="Wallet Key and API Key cannot be provided together"
        )

    # if an API key is provided verify it is valid
    if api_key:
        async with profile.session() as session:
            tenant_keys = await TenantAuthenticationApiRecord.query_by_tenant_id(
                session, tenant_id
            )
            LOGGER.warning(f"tenant_keys = {tenant_keys}")
            # if no keys found raise an error
            if not tenant_keys:
                raise web.HTTPUnauthorized(reason="API Key not found")
            # check if the provided key matches any of the tenant keys
            for tenant_key in tenant_keys:
                if mgr.check_api_key(api_key, tenant_key):
                    break
            else:
                raise web.HTTPUnauthorized(reason="API Key mismatch")

    # first look up the tenant...
    async with profile.session() as session:
        tenant_record = await TenantRecord.retrieve_by_id(session, tenant_id)

    # now just do the same wallet_id based token create.
    wallet_id = tenant_record.wallet_id
    multitenant_mgr = profile.inject(BaseMultitenantManager)
    async with profile.session() as session:
        wallet_record = await WalletRecord.retrieve_by_id(session, wallet_id)

    if (not wallet_record.requires_external_key) and wallet_key:
        LOGGER.warning(
            f"Wallet {wallet_id} doesn't require the wallet key but one was provided"
        )

    # Wallet key access use suppled, API key access used looked up key
    key = wallet_key if wallet_key else wallet_record.wallet_key
    token = await multitenant_mgr.create_auth_token(wallet_record, key)

    return web.json_response({"token": token})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@request_schema(ReservationRequestSchema())
@response_schema(ReservationResponseSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_tenant_reservation(request: web.BaseRequest):
    res = await tenant_reservation(request)
    return res


@docs(
    tags=[SWAGGER_CATEGORY],
)
@response_schema(DefaultConfigValuesSchema(), 200, description="")
@innkeeper_only
@error_handler
async def tenant_default_config_settings(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    mgr = context.inject(TenantManager)
    innkeeper_wallet_config: InnkeeperWalletConfig = mgr._config.innkeeper_wallet
    return web.json_response(
        {
            "connected_to_endorsers": list(
                endorser_config.serialize()
                for endorser_config in innkeeper_wallet_config.connect_to_endorser
            ),
            "created_public_did": innkeeper_wallet_config.create_public_did,
        }
    )


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(TenantIdMatchInfoSchema())
@request_schema(TenantConfigSchema())
@response_schema(TenantRecordSchema(), 200, description="")
@innkeeper_only
@error_handler
async def tenant_config_update(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    body = await request.json()
    connect_to_endorser = body.get("connect_to_endorser")
    create_public_did = body.get("create_public_did")
    enable_ledger_switch = body.get("enable_ledger_switch") or False
    curr_ledger_id = body.get("curr_ledger_id")
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    tenant_id = request.match_info["tenant_id"]
    async with profile.session() as session:
        tenant_record = await TenantRecord.retrieve_by_id(session, tenant_id)
        if connect_to_endorser or connect_to_endorser == []:
            tenant_record.connected_to_endorsers = connect_to_endorser
        if create_public_did or create_public_did == []:
            tenant_record.created_public_did = create_public_did
        if curr_ledger_id:
            tenant_record.curr_ledger_id = curr_ledger_id
        tenant_record.enable_ledger_switch = enable_ledger_switch
        await tenant_record.save(session)
    return web.json_response(tenant_record.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(ReservationIdMatchInfoSchema())
@request_schema(TenantConfigSchema())
@response_schema(ReservationRecordSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_tenant_res_update(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    body = await request.json()
    connect_to_endorser = body.get("connect_to_endorser")
    create_public_did = body.get("create_public_did")
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    reservation_id = request.match_info["reservation_id"]
    async with profile.session() as session:
        res_rec = await ReservationRecord.retrieve_by_reservation_id(
            session, reservation_id
        )
        if connect_to_endorser:
            res_rec.connect_to_endorsers = connect_to_endorser
        if create_public_did:
            res_rec.create_public_did = create_public_did
        await res_rec.save(session)
    return web.json_response(res_rec.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
)
@response_schema(ReservationListSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_reservations_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    tag_filter = {}
    post_filter = {}
    async with profile.session() as session:
        # innkeeper can access all reservation records
        records = await ReservationRecord.query(
            session=session,
            tag_filter=tag_filter,
            post_filter_positive=post_filter,
            alt=True,
        )
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(ReservationIdMatchInfoSchema())
@request_schema(ReservationApproveRequestSchema)
@response_schema(ReservationApproveResponseSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_reservations_approve(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    reservation_id = request.match_info["reservation_id"]

    body = await request.json()
    state_notes = body.get("state_notes")

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)

    try:
        _pwd = await approve_reservation(reservation_id, state_notes, mgr)
    except ReservationException as err:
        raise web.HTTPConflict(reason=str(err))

    return web.json_response({"reservation_pwd": _pwd})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(ReservationIdMatchInfoSchema())
@request_schema(ReservationRefreshSchema())
@response_schema(ReservationApproveResponseSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_reservations_refresh_password(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    reservation_id = request.match_info["reservation_id"]
    mgr = context.inject(TenantManager)
    try:
        _pwd = await refresh_registration_token(reservation_id, mgr)
    except ReservationException as err:
        raise web.HTTPConflict(reason=str(err))
    return web.json_response({"reservation_pwd": _pwd})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(ReservationIdMatchInfoSchema())
@request_schema(ReservationDenyRequestSchema)
@response_schema(ReservationResponseSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_reservations_deny(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    reservation_id = request.match_info["reservation_id"]

    body = await request.json()
    state_notes = body.get("state_notes")

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        # innkeeper can access all reservation records.
        rec = await ReservationRecord.retrieve_by_reservation_id(
            session, reservation_id, for_update=True
        )
        if rec.state == ReservationRecord.STATE_REQUESTED:
            rec.state_notes = state_notes
            rec.state = ReservationRecord.STATE_DENIED
            await rec.save(session)
            LOGGER.info(rec)
        else:
            raise web.HTTPConflict(
                reason=f"Reservation state is currently '{rec.state}' and cannot be set to '{ReservationRecord.STATE_DENIED}'."
            )

    return web.json_response(rec.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
)
@response_schema(TenantListSchema(), 200, description="")
@use_kwargs(TenantListQuerySchema(), location="query")
@innkeeper_only
@error_handler
async def innkeeper_tenants_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    # Get the state from query parameters, default to 'active'
    state = request.query.get("state", TenantRecord.STATE_ACTIVE)
    tag_filter = {}

    # If the state is not 'all', apply the filter
    if state != "all":
        tag_filter["state"] = state

    post_filter = {}

    async with profile.session() as session:
        # innkeeper can access all tenant records
        records = await TenantRecord.query(
            session=session,
            tag_filter=tag_filter,
            post_filter_positive=post_filter,
            alt=True,
        )
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(TenantIdMatchInfoSchema())
@response_schema(TenantRecordSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_tenant_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    tenant_id = request.match_info["tenant_id"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        # innkeeper can access all tenants..
        rec = await TenantRecord.retrieve_by_id(session, tenant_id)
        LOGGER.info(rec)

    return web.json_response(rec.serialize())


@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(TenantIdMatchInfoSchema())
@response_schema(TenantRecordSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_tenant_delete(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    tenant_id = request.match_info["tenant_id"]

    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        rec = await TenantRecord.retrieve_by_id(session, tenant_id)
        if rec:
            await rec.soft_delete(session)
            LOGGER.info("Tenant %s soft deleted.", tenant_id)
            return web.json_response({"success": f"Tenant {tenant_id} soft deleted."})
        else:
            raise web.HTTPNotFound(reason=f"Tenant {tenant_id} not found.")
    

@docs(
    tags=[SWAGGER_CATEGORY],
)
@match_info_schema(TenantIdMatchInfoSchema())
@request_schema(TenantConfigSchema())
@response_schema(TenantRecordSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_tenant_restore(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    tenant_id = request.match_info["tenant_id"]
    
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    
    async with profile.session() as session:
        rec = await TenantRecord.retrieve_by_id(session, tenant_id)
        if rec:
            if rec.state != TenantRecord.STATE_DELETED:
                raise web.HTTPBadRequest(reason=f"Tenant {tenant_id} is not deleted.")
            else:
                await rec.restore_deleted(session)
                LOGGER.info("Tenant %s has been restored.", tenant_id)
                return web.json_response({"success": f"Tenant {tenant_id} restored."})
        else:
            raise web.HTTPNotFound(reason=f"Tenant {tenant_id} not found.")
 

@docs(tags=[SWAGGER_CATEGORY], summary="Create API Key Record")
@request_schema(TenantAuthenticationsApiRequestSchema())
@response_schema(TenantAuthenticationsApiResponseSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_authentications_api(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    body = await request.json()
    rec: TenantAuthenticationApiRecord = TenantAuthenticationApiRecord(**body)

    # keys are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    try:
        api_key, tenant_authentication_api_id = await create_api_key(rec, mgr)
    except TenantApiKeyException as err:
        raise web.HTTPConflict(reason=str(err))

    return web.json_response(
        {
            "tenant_authentication_api_id": tenant_authentication_api_id,
            "api_key": api_key,
        }
    )


@docs(tags=[SWAGGER_CATEGORY], summary="List all API Key Records")
@response_schema(TenantAuthenticationApiListSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_authentications_api_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    tag_filter = {}
    post_filter = {}
    async with profile.session() as session:
        # innkeeper can access all reservation records
        records = await TenantAuthenticationApiRecord.query(
            session=session,
            tag_filter=tag_filter,
            post_filter_positive=post_filter,
            alt=True,
        )
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


@docs(tags=[SWAGGER_CATEGORY], summary="Read API Key Record")
@match_info_schema(TenantAuthenticationApiIdMatchInfoSchema())
@response_schema(TenantAuthenticationApiRecordSchema(), 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_authentications_api_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    tenant_authentication_api_id = request.match_info["tenant_authentication_api_id"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    async with profile.session() as session:
        # innkeeper can access all tenants..
        rec = await TenantAuthenticationApiRecord.retrieve_by_auth_api_id(
            session, tenant_authentication_api_id
        )
        LOGGER.info(rec)

    return web.json_response(rec.serialize())


@docs(tags=[SWAGGER_CATEGORY], summary="Delete API Key")
@match_info_schema(TenantAuthenticationApiIdMatchInfoSchema)
@response_schema(TenantAuthenticationApiOperationResponseSchema, 200, description="")
@innkeeper_only
@error_handler
async def innkeeper_authentications_api_delete(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    tenant_authentication_api_id = request.match_info["tenant_authentication_api_id"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    result = False
    async with profile.session() as session:
        rec = await TenantAuthenticationApiRecord.retrieve_by_auth_api_id(
            session, tenant_authentication_api_id
        )

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
@innkeeper_only
@error_handler
async def innkeeper_config_handler(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    # use base/root profile for server config, use Tenant Manager profile
    # this is to not get the Innkeeper tenant's config, but the server cfg
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    config = {
        key: (
           profile.context.settings[key]
        )
        for key in profile.context.settings
        if key
        not in [
            "admin.admin_api_key",
            "multitenant.jwt_secret",
            "wallet.key",
            "wallet.rekey",
            "wallet.seed",
            "wallet.storage_creds",
        ]
    }
    try:
      del config["plugin_config"]["traction_innkeeper"]["innkeeper_wallet"]["wallet_key"]
    except KeyError as e:
      LOGGER.warn(f"The key to be removed: '{e.args[0]}' is missing from the dictionary.")
    config["version"] = __version__

    return web.json_response({"config": config})


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    # routes that do not require a tenant token can be easily slotted under multitenancy.
    app.add_routes(
        [
            web.post("/multitenancy/reservations", tenant_reservation),
            web.get(
                "/multitenancy/reservations/{reservation_id}",
                tenant_reservation_get,
                allow_head=False,
            ),
            web.post(
                "/multitenancy/reservations/{reservation_id}/check-in", tenant_checkin
            ),
            web.post("/multitenancy/tenant/{tenant_id}/token", tenant_create_token),
        ]
    )
    # routes that require a tenant token for the innkeeper wallet/tenant/agent.
    # these require not only a tenant, but it has to be the innkeeper tenant!
    app.add_routes(
        [
            web.post("/innkeeper/reservations", innkeeper_tenant_reservation),
            web.get(
                "/innkeeper/reservations/",
                innkeeper_reservations_list,
                allow_head=False,
            ),
            web.put(
                "/innkeeper/reservations/{reservation_id}/approve",
                innkeeper_reservations_approve,
            ),
            web.put(
                "/innkeeper/reservations/{reservation_id}/config",
                innkeeper_tenant_res_update,
            ),
            web.put(
                "/innkeeper/reservations/{reservation_id}/deny",
                innkeeper_reservations_deny,
            ),
            web.put(
                "/innkeeper/reservations/{reservation_id}/refresh-password",
                innkeeper_reservations_refresh_password,
            ),
            web.get("/innkeeper/tenants/", innkeeper_tenants_list, allow_head=False),
            web.get(
                "/innkeeper/tenants/{tenant_id}", innkeeper_tenant_get, allow_head=False
            ),
            web.put("/innkeeper/tenants/{tenant_id}/config", tenant_config_update),
            web.delete("/innkeeper/tenants/{tenant_id}", innkeeper_tenant_delete),
            web.put("/innkeeper/tenants/{tenant_id}/restore", innkeeper_tenant_restore),
            web.get(
                "/innkeeper/default-config",
                tenant_default_config_settings,
                allow_head=False,
            ),
            web.post("/innkeeper/authentications/api", innkeeper_authentications_api),
            web.get(
                "/innkeeper/authentications/api/",
                innkeeper_authentications_api_list,
                allow_head=False,
            ),
            web.get(
                "/innkeeper/authentications/api/{tenant_authentication_api_id}",
                innkeeper_authentications_api_get,
                allow_head=False,
            ),
            web.delete(
                "/innkeeper/authentications/api/{tenant_authentication_api_id}",
                innkeeper_authentications_api_delete,
            ),
            web.get(
                "/innkeeper/server/status/config",
                innkeeper_config_handler,
                allow_head=False,
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
            "description": "Traction Innkeeper - manage tenants (traction_innkeeper v1_0 plugin)",
        }
    )
