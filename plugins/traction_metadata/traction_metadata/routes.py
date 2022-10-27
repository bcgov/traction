import logging

from aiohttp import web
from aiohttp_apispec import docs, request_schema, response_schema

from marshmallow import fields

from aries_cloudagent.messaging.models.openapi import OpenAPISchema


LOGGER = logging.getLogger(__name__)

class MetadataModuleResponseSchema(OpenAPISchema):
    """Response schema for demo"""


class MetadataModuleSchema(OpenAPISchema):
    """Request schema for demo"""
    content = fields.Str(description="Message content", example="Metadata!")


@docs(tags=["demo"], summary="just a dummy endpoint to show traction_metadata plugin loaded")
@request_schema(MetadataModuleSchema())
@response_schema(MetadataModuleResponseSchema(), 200, description="")
async def hello_world(request: web.BaseRequest):
    LOGGER.info(request)
    params = await request.json()
    return web.json_response({"message": f"Hello {params['content']}!"})

async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    app.add_routes(
        [web.post("/demo/traction_metadata/hello-world", hello_world)]
    )
    LOGGER.info("< registering routes")


def post_process_routes(app: web.Application):
    """Amend swagger API."""

    # Add top-level tags description
    if "tags" not in app._state["swagger_dict"]:
        app._state["swagger_dict"]["tags"] = []
    app._state["swagger_dict"]["tags"].append(
        {
            "name": "demo",
            "description": "Traction plugins demo",
        }
    )
