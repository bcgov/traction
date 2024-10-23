import logging

from aiohttp import web
from acapy_agent.utils.classloader import ClassLoader

from . import MODULES

LOGGER = logging.getLogger(__name__)


def load_routes(module_name):
    LOGGER.info(f"> load_routes({module_name})")
    try:
        routes = ClassLoader.load_module("routes", module_name)
    except Exception as err:
        LOGGER.warning(f"Error loading routes for {module_name}: {err}")
        routes = None
        
    LOGGER.info(f"< load_routes({module_name}): {routes}")
    return routes


async def register(app: web.Application):
    """Register routes."""
    LOGGER.info("> register routes")
    # perform a pseudo load of the other "plugins"
    #
    # See notes in __init__.py setup.
    for mod in MODULES:
        routes = load_routes(mod.__name__)
        if routes:
            try:
                await routes.register(app)
            except Exception as err:
                LOGGER.error(f"error registering routes for {mod.__name__}", err)

    LOGGER.info("< register routes")


def post_process_routes(app: web.Application):
    LOGGER.info("> post-process routes")
    for mod in MODULES:
        routes = load_routes(mod.__name__)
        if routes:
            try:
                routes.post_process_routes(app)
            except Exception as err:
                LOGGER.warning(
                    f"error post processing routes for {mod.__name__}: {err}"
                )

    LOGGER.info("< post-process routes")
