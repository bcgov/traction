import functools
import logging

from aiohttp import web
from aiohttp_apispec import (
    docs,
    response_schema,
    request_schema,
    querystring_schema,
    match_info_schema,
)
from acapy_agent.admin.request_context import AdminRequestContext
from acapy_agent.messaging.models.base import BaseModelError
from acapy_agent.messaging.models.openapi import OpenAPISchema
from acapy_agent.messaging.valid import (
    INDY_SCHEMA_ID_EXAMPLE,
    INDY_SCHEMA_ID_VALIDATE,
    INDY_CRED_DEF_ID_EXAMPLE,
    INDY_CRED_DEF_ID_VALIDATE,
    UUIDFour,
)
from acapy_agent.storage.error import StorageNotFoundError, StorageError
from acapy_agent.admin.decorators.auth import tenant_authentication
from marshmallow import fields, ValidationError

from . import OcaService
from .models import OcaRecordSchema
from .oca_service import PublicDIDRequiredError, PublicDIDMismatchError

LOGGER = logging.getLogger(__name__)

SWAGGER_CATEGORY = "oca"


def error_handler(func):
    @functools.wraps(func)
    async def wrapper(request):
        try:
            ret = await func(request)
            return ret
        except ValidationError as err:
            raise web.HTTPUnprocessableEntity(reason=err.messages) from err
        except PublicDIDRequiredError as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err
        except PublicDIDMismatchError as err:
            raise web.HTTPUnauthorized(reason=err.roll_up) from err
        except StorageNotFoundError as err:
            raise web.HTTPNotFound(reason=err.roll_up) from err
        except (StorageError, BaseModelError) as err:
            raise web.HTTPBadRequest(reason=err.roll_up) from err
        except Exception as err:
            LOGGER.error(err)
            raise err

    return wrapper


class OcaRecordListQueryStringSchema(OpenAPISchema):
    cred_def_id = fields.Str(
        required=False, description="Cred Def identifier", 
        example=INDY_CRED_DEF_ID_EXAMPLE, 
        validate=INDY_CRED_DEF_ID_VALIDATE
    )


class OcaRecordListSchema(OpenAPISchema):
    """Response schema for oca list."""

    results = fields.List(
        fields.Nested(OcaRecordSchema()),
        description="List of OCA records",
    )


class AddOcaRecordRequestSchema(OpenAPISchema):
    """Request schema for adding oca record link."""

    schema_id = fields.Str(
        required=False,
        description="Schema identifier",
        validate=INDY_SCHEMA_ID_VALIDATE,
        example=INDY_SCHEMA_ID_EXAMPLE,
    )
    cred_def_id = fields.Str(
        required=False,
        description="Cred Def identifier",
        validate=INDY_CRED_DEF_ID_VALIDATE,
        example=INDY_CRED_DEF_ID_EXAMPLE,
    )
    url = fields.Str(required=False, description="(Public) Url for OCA Bundle")
    bundle = fields.Dict(
        required=False,
        description="OCA Bundle",
    )


class OcaIdMatchInfoSchema(OpenAPISchema):
    oca_id = fields.Str(
        description="OCA Record identifier", required=True, example=UUIDFour.EXAMPLE
    )


class OcaRecordOperationResponseSchema(OpenAPISchema):
    """Response schema for simple operations."""

    success = fields.Bool(
        required=True,
        description="True if operation successful, false if otherwise",
    )


@docs(tags=[SWAGGER_CATEGORY], summary="Add OCA Record")
@request_schema(AddOcaRecordRequestSchema())
@response_schema(OcaRecordSchema(), 200, description="")
@error_handler
@tenant_authentication
async def oca_record_create(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    service = context.inject(OcaService)

    body = await request.json()
    rec = await service.create_or_update_oca_record(context.profile, body)

    return web.json_response(rec.serialize())


@docs(tags=[SWAGGER_CATEGORY], summary="Read OCA Record")
@match_info_schema(OcaIdMatchInfoSchema())
@response_schema(OcaRecordSchema(), 200, description="")
@error_handler
@tenant_authentication
async def oca_record_read(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    service = context.inject(OcaService)

    oca_id = request.match_info["oca_id"]
    rec = await service.read_oca_record(context.profile, oca_id)
    LOGGER.info(f"rec = {rec}")
    return web.json_response(rec.serialize())


@docs(tags=[SWAGGER_CATEGORY], summary="Update OCA Record")
@match_info_schema(OcaIdMatchInfoSchema())
@request_schema(OcaRecordSchema())
@response_schema(OcaRecordSchema(), 200, description="")
@error_handler
@tenant_authentication
async def oca_record_update(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    service = context.inject(OcaService)

    oca_id = request.match_info["oca_id"]
    body = await request.json()
    rec = await service.update_oca_record(context.profile, oca_id, body)
    return web.json_response(rec.serialize())


@docs(tags=[SWAGGER_CATEGORY], summary="Delete OCA Record")
@match_info_schema(OcaIdMatchInfoSchema())
@response_schema(OcaRecordOperationResponseSchema, 200, description="")
@error_handler
@tenant_authentication
async def oca_record_delete(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    service = context.inject(OcaService)
    oca_id = request.match_info["oca_id"]
    success = await service.delete_oca_record(context.profile, oca_id)
    return web.json_response({"success": success})


@docs(
    tags=[SWAGGER_CATEGORY],
)
@querystring_schema(OcaRecordListQueryStringSchema())
@response_schema(OcaRecordListSchema(), 200, description="")
@error_handler
@tenant_authentication
async def oca_record_list(request: web.BaseRequest):
    context: AdminRequestContext = request["context"]
    service = context.inject(OcaService)
    cred_def_id = request.query.get("cred_def_id")
    records = await service.list_oca_records(context.profile, None, cred_def_id)
    results = [record.serialize() for record in records]

    return web.json_response({"results": results})


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    app.add_routes(
        [
            web.get("/oca", oca_record_list, allow_head=False),
            web.post("/oca", oca_record_create),
            web.get("/oca/{oca_id}", oca_record_read, allow_head=False),
            web.put("/oca/{oca_id}", oca_record_update),
            web.delete("/oca/{oca_id}", oca_record_delete),
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
            "description": "OCA Bundles - manage OCA Bundles (traction_innkeeper v1_0 plugin)",
        }
    )
