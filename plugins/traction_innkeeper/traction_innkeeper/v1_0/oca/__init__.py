import logging

from acapy_agent.admin.base_server import BaseAdminServer
from acapy_agent.admin.server import AdminServer
from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.core.event_bus import EventBus, Event
from acapy_agent.core.plugin_registry import PluginRegistry
from acapy_agent.core.profile import Profile
from acapy_agent.core.protocol_registry import ProtocolRegistry
from acapy_agent.core.util import STARTUP_EVENT_PATTERN

from .oca_service import OcaService

LOGGER = logging.getLogger(__name__)


async def setup(context: InjectionContext):
    LOGGER.info("> plugin setup...")

    protocol_registry = context.inject(ProtocolRegistry)
    if not protocol_registry:
        raise ValueError("ProtocolRegistry missing in context")

    plugin_registry = context.inject(PluginRegistry)
    if not plugin_registry:
        raise ValueError("PluginRegistry missing in context")

    bus = context.inject(EventBus)
    if not bus:
        raise ValueError("EventBus missing in context")

    bus.subscribe(STARTUP_EVENT_PATTERN, on_startup)

    LOGGER.info("< plugin setup.")


async def on_startup(profile: Profile, event: Event):
    LOGGER.info("> on_startup")
    svc = OcaService(profile)
    profile.context.injector.bind_instance(OcaService, svc)

    OCA_PATH = "/oca"

    srv: AdminServer = profile.context.inject(BaseAdminServer)

    # see if any other base wallet routes were added...
    base_wallet_routes = profile.context.settings.get("multitenant.base_wallet_routes")
    LOGGER.info(f"base_wallet_routes = {base_wallet_routes}")
    if base_wallet_routes is None:
        base_wallet_routes = []
    if OCA_PATH not in base_wallet_routes:
        base_wallet_routes.append(OCA_PATH)
    # now add set the "configuration"
    profile.context.settings.set_value(
        "multitenant.base_wallet_routes", base_wallet_routes
    )
    # and we need to tell the server to load the additional routes
    # first call to this property "builds" the underlying property...
    srv.additional_routes_pattern
    # our pattern should be known to the server now...
    # second call to the property should return all the patterns it will use
    LOGGER.info(f"srv.additional_routes_pattern = {srv.additional_routes_pattern}")
    LOGGER.info("< on_startup")
