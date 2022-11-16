import logging


from aiohttp import web


LOGGER = logging.getLogger(__name__)
SWAGGER_INNKEEPER = "traction-innkeeper"
SWAGGER_TENANT = "traction-tenant"


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> registering routes")
    app.add_routes([])
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
