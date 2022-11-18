import functools
import logging
import uuid

import bcrypt
from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema, match_info_schema
from aries_cloudagent.admin.request_context import AdminRequestContext
from aries_cloudagent.messaging.models.base import BaseModelError
from aries_cloudagent.messaging.models.openapi import OpenAPISchema
from aries_cloudagent.messaging.valid import UUIDFour, JSONWebToken
from aries_cloudagent.storage.error import StorageError
from marshmallow import fields

from . import TenantManager
from .models import (
    ReservationRecordSchema,
    ReservationRecord,
    TenantRecord,
    TenantRecordSchema,
)

LOGGER = logging.getLogger(__name__)
SWAGGER_INNKEEPER = "traction-innkeeper"
SWAGGER_TENANT = "traction-tenant"

SALT = b"$2b$12$xnIis84MXfK8E4B3Qrmkne"  # get from settings.


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


class ReservationResponseSchema(ReservationRecordSchema):
    """Response schema for tenant reservation."""


class SigninSchema(OpenAPISchema):
    """Request schema for tenant signin."""

    reservation_pwd = fields.Str(
        required=True,
        description="The reservation password",
    )


class SigninResponseSchema(OpenAPISchema):
    """Response schema for tenant signin."""

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
async def tenant_reservation(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    body = await request.json()
    rec: ReservationRecord = ReservationRecord(**body)

    # reservations are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    try:
        async with profile.session() as session:
            await rec.save(session, reason="New tenant reservation")
            LOGGER.info(rec)
    except Exception as err:
        LOGGER.error(err)
        raise err

    return web.json_response(rec.serialize())


@docs(
    tags=["multitenancy"],
)
@request_schema(SigninSchema())
@response_schema(SigninResponseSchema(), 200, description="")
async def tenant_signin(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    body = await request.json()

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    reservation_pwd = body.get("reservation_pwd")
    reservation_token = bcrypt.hashpw(reservation_pwd.encode("utf-8"), SALT)
    if bcrypt.checkpw(reservation_pwd.encode("utf-8"), reservation_token):
        # we should be able to get the record since we have the correct pwd...
        try:
            async with profile.session() as session:
                res_rec = await ReservationRecord.query_by_reservation_token(
                    session, reservation_token.decode("utf-8")
                )
                if res_rec.state == ReservationRecord.STATE_APPROVED:
                    # ok, let's update this, create a tenant, create a wallet
                    tenant, wallet_record, token = await mgr.create_wallet(
                        res_rec.tenant_name
                    )

                    # update this reservation
                    res_rec.state = ReservationRecord.STATE_COMPLETED
                    res_rec.wallet_id = wallet_record.wallet_id
                    res_rec.tenant_id = tenant.tenant_id
                    res_rec.reservation_token = None
                    await res_rec.save(session)
        except Exception as err:
            LOGGER.error(err)
            raise err

    return web.json_response(
        {
            "wallet_id": wallet_record.wallet_id,
            "wallet_key": wallet_record.wallet_key,
            "token": token,
        }
    )


@docs(
    tags=[SWAGGER_INNKEEPER],
)
@response_schema(ReservationListSchema(), 200, description="")
@innkeeper_only
async def innkeeper_reservations_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    tag_filter = {}
    post_filter = {}
    try:
        async with profile.session() as session:
            # innkeeper can access all reservation records
            records = await ReservationRecord.query(
                session=session,
                tag_filter=tag_filter,
                post_filter_positive=post_filter,
                alt=True,
            )
        results = [record.serialize() for record in records]
    except (StorageError, BaseModelError) as err:
        raise web.HTTPBadRequest(reason=err.roll_up) from err

    return web.json_response({"results": results})


@docs(
    tags=[SWAGGER_INNKEEPER],
)
@match_info_schema(ReservationIdMatchInfoSchema())
@response_schema(ReservationApproveResponseSchema(), 200, description="")
@innkeeper_only
async def innkeeper_reservations_approve(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    reservation_id = request.match_info["reservation_id"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    try:
        async with profile.session() as session:
            # innkeeper can access all reservation records.
            rec = await ReservationRecord.retrieve_by_id(
                session, reservation_id, for_update=True
            )
            if rec.state == ReservationRecord.STATE_REQUESTED:
                # create the token...
                reservation_pwd = str(uuid.uuid4())  # we need to return this...
                reservation_token = bcrypt.hashpw(reservation_pwd.encode("utf-8"), SALT)
                rec.reservation_token = reservation_token.decode("utf-8")
                rec.state = ReservationRecord.STATE_APPROVED
                await rec.save(session)
            LOGGER.info(rec)
    except Exception as err:
        LOGGER.error(err)
        raise err

    return web.json_response({"reservation_pwd": reservation_pwd})


@docs(
    tags=[SWAGGER_INNKEEPER],
)
@response_schema(TenantListSchema(), 200, description="")
@innkeeper_only
async def innkeeper_tenants_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile

    tag_filter = {}
    post_filter = {}
    try:
        async with profile.session() as session:
            # innkeeper can access all tenant records
            records = await TenantRecord.query(
                session=session,
                tag_filter=tag_filter,
                post_filter_positive=post_filter,
                alt=True,
            )
        results = [record.serialize() for record in records]
    except (StorageError, BaseModelError) as err:
        raise web.HTTPBadRequest(reason=err.roll_up) from err

    return web.json_response({"results": results})


@docs(
    tags=[SWAGGER_INNKEEPER],
)
@match_info_schema(TenantIdMatchInfoSchema())
@response_schema(TenantRecordSchema(), 200, description="")
@innkeeper_only
async def innkeeper_tenant_get(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    tenant_id = request.match_info["tenant_id"]

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    try:
        async with profile.session() as session:
            # innkeeper can access all tenants..
            rec = await TenantRecord.retrieve_by_id(session, tenant_id)
            LOGGER.info(rec)
    except Exception as err:
        LOGGER.error(err)
        raise err

    return web.json_response(rec.serialize())


@docs(
    tags=[SWAGGER_TENANT],
)
@response_schema(TenantRecordSchema(), 200, description="")
async def tenant_self(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    # we need the caller's wallet id
    wallet_id = context.profile.settings.get("wallet.id")

    # records are under base/root profile, use Tenant Manager profile
    mgr = context.inject(TenantManager)
    profile = mgr.profile
    try:
        async with profile.session() as session:
            # tenant's must always fetch by their wallet id.
            rec = await TenantRecord.query_by_wallet_id(session, wallet_id)
            LOGGER.info(rec)
    except Exception as err:
        LOGGER.error(err)
        raise err

    return web.json_response(rec.serialize())


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    # routes that do not require a tenant token can be easily slotted under multitenancy.
    app.add_routes(
        [
            web.post("/multitenancy/tenant/reservation", tenant_reservation),
            web.post("/multitenancy/tenant/signin", tenant_signin),
        ]
    )
    # routes that require a tenant token.
    app.add_routes(
        [
            web.get("/tenant", tenant_self, allow_head=False),
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
            "name": SWAGGER_INNKEEPER,
            "description": "Traction Innkeeper - manage tenants (traction_innkeeper v1_0 plugin)",
        }
    )
    app._state["swagger_dict"]["tags"].append(
        {
            "name": SWAGGER_TENANT,
            "description": "Traction Tenant - tenant self administration (traction_innkeeper v1_0 plugin)",
        }
    )
