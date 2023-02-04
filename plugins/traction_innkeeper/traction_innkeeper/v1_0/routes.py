import functools
import json
import logging
import uuid

from aiohttp import web
from aiohttp_apispec import (
    docs,
    request_schema,
    response_schema,
    match_info_schema,
)
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.valid import (
    UUIDFour,
    JSONWebToken,
    INDY_DID,
    INDY_RAW_PUBLIC_KEY,
)
from aries_cloudagent.multitenant.admin.routes import (
    CreateWalletTokenRequestSchema,
    CreateWalletTokenResponseSchema,
)
from aries_cloudagent.multitenant.base import BaseMultitenantManager
from aries_cloudagent.multitenant.error import WalletKeyMissingError
from aries_cloudagent.storage.error import StorageError, StorageNotFoundError
from aries_cloudagent.wallet.error import WalletSettingsError
from aries_cloudagent.wallet.models.wallet_record import WalletRecord
from marshmallow import fields

from . import TenantManager
from .models import (
    ReservationRecordSchema,
    ReservationRecord,
    TenantRecord,
    TenantRecordSchema,
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


class ReservationRequestSchema(OpenAPISchema):
    """Request schema for tenant reservation."""

    tenant_name = fields.Str(
        required=True,
        description="Proposed name of Tenant",
        example="line of business short name",
    )

    tenant_reason = fields.Str(
        required=True,
        description="Reason(s) for requesting a tenant",
        example="Issue permits to clients",
    )

    contact_name = fields.Str(
        required=True,
        description="Contact name for this tenant request",
    )

    contact_email = fields.Str(
        required=True,
        description="Contact email for this tenant request",
    )

    contact_phone = fields.Str(
        required=True,
        description="Contact phone number for this tenant request",
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


class TenantListSchema(OpenAPISchema):
    """Response schema for tenants list."""

    results = fields.List(
        fields.Nested(TenantRecordSchema()),
        description="List of tenants",
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
        rec = await ReservationRecord.retrieve_by_id(session, reservation_id)
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
        res_rec = await ReservationRecord.retrieve_by_id(session, reservation_id)
        reservation_pwd = body.get("reservation_pwd")

        if res_rec.expired:
            raise web.HTTPUnauthorized(reason="Reservation has expired")

        if res_rec.state == ReservationRecord.STATE_APPROVED:
            reservation_token = mgr.check_reservation_password(reservation_pwd, res_rec)
            if not reservation_token:
                raise web.HTTPUnauthorized(reason="Reservation password incorrect")

            # ok, let's update this, create a tenant, create a wallet
            wallet_key = str(uuid.uuid4())
            tenant, wallet_record, token = await mgr.create_wallet(
                res_rec.tenant_name, wallet_key
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
@request_schema(CreateWalletTokenRequestSchema)
@response_schema(CreateWalletTokenResponseSchema(), 200, description="")
@error_handler
async def tenant_create_token(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    tenant_id = request.match_info["tenant_id"]
    wallet_key = None

    if request.body_exists:
        body = await request.json()
        wallet_key = body.get("wallet_key")

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

    token = await multitenant_mgr.create_auth_token(wallet_record, wallet_key)

    return web.json_response({"token": token})


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
    profile = mgr.profile

    async with profile.session() as session:
        # innkeeper can access all reservation records.
        rec = await ReservationRecord.retrieve_by_id(
            session, reservation_id, for_update=True
        )
        if rec.state == ReservationRecord.STATE_REQUESTED:
            _pwd, _salt, _hash, _expiry = mgr.generate_reservation_token_data()
            rec.reservation_token_salt = _salt.decode("utf-8")
            rec.reservation_token_hash = _hash.decode("utf-8")
            rec.reservation_token_expiry = _expiry
            rec.state_notes = state_notes
            rec.state = ReservationRecord.STATE_APPROVED
            await rec.save(session)
            LOGGER.info(rec)
        else:
            raise web.HTTPConflict(
                reason=f"Reservation state is currently '{rec.state}' and cannot be set to '{ReservationRecord.STATE_APPROVED}'."
            )

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
        rec = await ReservationRecord.retrieve_by_id(
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
@innkeeper_only
@error_handler
async def innkeeper_tenants_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    tag_filter = {}
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
                "/innkeeper/reservations/{reservation_id}/deny",
                innkeeper_reservations_deny,
            ),
            web.get("/innkeeper/tenants/", innkeeper_tenants_list, allow_head=False),
            web.get(
                "/innkeeper/tenants/{tenant_id}", innkeeper_tenant_get, allow_head=False
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
